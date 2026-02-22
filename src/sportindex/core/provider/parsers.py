"""
Parser functions for complex Sofascore API transformations.

These functions contain the logic that genuinely earns its keep:
reconstructing period structures, dispatching incidents, extracting
derived values, and converting timestamps/ISO strings to proper
datetime/date objects.

All functions take raw dicts (as returned by the API / provider)
and return typed dicts (see types.py for output shapes).
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from typing import Any, Literal, overload

from .types import (
    ParsedCardIncident,
    ParsedExtraTimeIncident,
    ParsedGoalIncident,
    ParsedIncident,
    ParsedPenaltyIncident,
    ParsedPenaltyShootoutIncident,
    ParsedPeriod,
    ParsedPeriodIncident,
    ParsedPeriods,
    ParsedScore,
    ParsedSubstitutionIncident,
    ParsedVarDecisionIncident,
)

logger = logging.getLogger(__name__)


# =====================================================================
# Date / Datetime utilities
# =====================================================================

@overload
def timestamp_to_dt(ts: None, *, kind: Literal["date"]) -> None: ...
@overload
def timestamp_to_dt(ts: None, *, kind: Literal["datetime"]) -> None: ...
@overload
def timestamp_to_dt(ts: int | float, *, kind: Literal["date"]) -> date: ...
@overload
def timestamp_to_dt(ts: int | float, *, kind: Literal["datetime"]) -> datetime: ...

def timestamp_to_dt(
    ts: int | float | None,
    *,
    kind: Literal["date", "datetime"] = "datetime",
) -> datetime | date | None:
    """Convert a Unix timestamp to a datetime (UTC) or date object.

    Returns None if `ts` is None.
    """
    if ts is None:
        return None
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    if kind == "date":
        return dt.date()
    return dt


@overload
def iso_to_dt(value: None, *, kind: Literal["date"]) -> None: ...
@overload
def iso_to_dt(value: None, *, kind: Literal["datetime"]) -> None: ...
@overload
def iso_to_dt(value: str, *, kind: Literal["date"]) -> date: ...
@overload
def iso_to_dt(value: str, *, kind: Literal["datetime"]) -> datetime: ...

def iso_to_dt(
    value: str | None,
    *,
    kind: Literal["date", "datetime"] = "datetime",
) -> datetime | date | None:
    """Convert an ISO 8601 string to a datetime (UTC) or date object.

    If the input has no timezone info, UTC is assumed.
    Returns None if `value` is None.
    """
    if value is None:
        return None
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    if kind == "date":
        return dt.date()
    return dt


# =====================================================================
# Helpers — nested access
# =====================================================================

def get_nested(data: dict, path: str, default: Any = None) -> Any:
    """Dot-path access into a nested dict. E.g. get_nested(d, "a.b.c")."""
    current = data
    for key in path.split("."):
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


# =====================================================================
# Event helpers
# =====================================================================

OUTCOME_MAPPING: dict[int, str] = {
    1: "home",
    2: "away",
    3: "draw",
}

WINNER_MAPPING: dict[int, str] = {
    1: "home",
    2: "away",
    3: "tied",
}


def get_event_outcome(raw_event: dict[str, Any]) -> str | None:
    """Extract the outcome of an event from `winnerCode`.

    Returns "home", "away", "draw", or None if not available.
    """
    return OUTCOME_MAPPING.get(raw_event.get("winnerCode"))


def get_display_score(raw_event: dict[str, Any]) -> ParsedScore | None:
    """Extract the display score from a raw event dict.

    Returns {"home": int, "away": int} or None if scores are missing.
    """
    home_score = raw_event.get("homeScore", {})
    away_score = raw_event.get("awayScore", {})
    if "display" in home_score and "display" in away_score:
        return ParsedScore(home=home_score["display"], away=away_score["display"])
    return None


# =====================================================================
# Incident parsing — full polymorphic dispatch
# =====================================================================

KNOWN_INCIDENT_TYPES = frozenset({
    "goal",
    "penalty",
    "penaltyShootout",
    "card",
    "period",
    "varDecision",
    "substitution",
    "injuryTime",
})


def _get_side(raw: dict[str, Any]) -> str | None:
    """Convert `isHome` boolean to "home" / "away" / None."""
    if "isHome" not in raw:
        return None
    return "home" if raw["isHome"] else "away"


def _get_score(raw: dict[str, Any]) -> ParsedScore | None:
    """Extract running score from an incident (flat homeScore/awayScore ints)."""
    if "homeScore" in raw and "awayScore" in raw:
        return ParsedScore(home=raw["homeScore"], away=raw["awayScore"])
    return None


# -- Per-type parsers --------------------------------------------------

def _parse_goal(raw: dict[str, Any]) -> ParsedGoalIncident:
    return ParsedGoalIncident(
        incidentType="goal",
        id=raw.get("id"),
        time=raw.get("time"),
        side=_get_side(raw),
        score=_get_score(raw),
        scorer=raw.get("player"),        # raw player dict, kept as-is
        assist=raw.get("assist"),         # raw player dict or None
        extraTime=raw.get("addedTime"),
        kind=raw.get("incidentClass"),    # "regular", "ownGoal", "penalty", "try", "twoPoints"...
    )


def _parse_penalty(raw: dict[str, Any]) -> ParsedPenaltyIncident:
    """Missed in-play penalty (scored ones arrive as goal incidents)."""
    return ParsedPenaltyIncident(
        incidentType="penalty",
        id=raw.get("id"),
        time=raw.get("time"),
        side=_get_side(raw),
        shooter=raw.get("player"),
        extraTime=raw.get("addedTime"),
        description=raw.get("description"),
        kind=raw.get("incidentClass"),
    )


def _parse_penalty_shootout(raw: dict[str, Any]) -> ParsedPenaltyShootoutIncident:
    return ParsedPenaltyShootoutIncident(
        incidentType="penaltyShootout",
        id=raw.get("id"),
        side=_get_side(raw),
        score=_get_score(raw),
        shooter=raw.get("player"),
        kind=raw.get("incidentClass"),    # "scored", "missed"
    )


def _parse_card(raw: dict[str, Any]) -> ParsedCardIncident:
    # Card can be given to a player OR a manager — resolve which one
    if raw.get("player"):
        recipient = raw["player"]
        recipient_type = "player"
    else:
        recipient = raw.get("manager")
        recipient_type = "manager"

    return ParsedCardIncident(
        incidentType="card",
        id=raw.get("id"),
        time=raw.get("time"),             # -5 means card given on bench
        side=_get_side(raw),
        recipient=recipient,
        recipientType=recipient_type,
        rescinded=raw.get("rescinded", False),
        reason=raw.get("reason"),
        extraTime=raw.get("addedTime"),
        kind=raw.get("incidentClass"),    # "yellow", "red", "yellowRed"
    )


def _parse_period(raw: dict[str, Any]) -> ParsedPeriodIncident:
    # API sends time=999 for "no meaningful time" → normalise to None
    time = raw.get("time")
    if time == 999:
        time = None

    return ParsedPeriodIncident(
        incidentType="period",
        time=time,
        score=_get_score(raw),
        kind=raw.get("text"),             # "HT", "FT", "PEN", etc.
    )


def _parse_var_decision(raw: dict[str, Any]) -> ParsedVarDecisionIncident:
    return ParsedVarDecisionIncident(
        incidentType="varDecision",
        id=raw.get("id"),
        time=raw.get("time"),
        side=_get_side(raw),
        extraTime=raw.get("addedTime"),
        description=raw.get("text"),
        kind=raw.get("incidentClass"),    # "goalAwarded", "penaltyCheck", etc.
        confirmed=raw.get("confirmed"),
    )


def _parse_substitution(raw: dict[str, Any]) -> ParsedSubstitutionIncident:
    return ParsedSubstitutionIncident(
        incidentType="substitution",
        id=raw.get("id"),
        time=raw.get("time"),
        side=_get_side(raw),
        playerIn=raw.get("playerIn"),     # raw player dict
        playerOut=raw.get("playerOut"),    # raw player dict
        extraTime=raw.get("addedTime"),
        kind=raw.get("incidentClass"),    # "regular", "injury"
    )


def _parse_extra_time(raw: dict[str, Any]) -> ParsedExtraTimeIncident:
    return ParsedExtraTimeIncident(
        incidentType="injuryTime",
        time=raw.get("time"),
        addedTime=raw.get("length"),      # minutes of added time
    )


# Dispatch table
_INCIDENT_PARSERS: dict[str, Any] = {
    "goal": _parse_goal,
    "penalty": _parse_penalty,
    "penaltyShootout": _parse_penalty_shootout,
    "card": _parse_card,
    "period": _parse_period,
    "varDecision": _parse_var_decision,
    "substitution": _parse_substitution,
    "injuryTime": _parse_extra_time,
}


def parse_incident(raw: dict[str, Any]) -> ParsedIncident | None:
    """Parse a single raw incident into a typed dict.

    Returns None if the incident type is unknown (and logs a warning).
    """
    incident_type = raw.get("incidentType")
    parser = _INCIDENT_PARSERS.get(incident_type)
    if parser is None:
        logger.warning(
            f"Unknown incident type '{incident_type}' — skipping. "
            f"Add a parser to _INCIDENT_PARSERS if it should be handled."
        )
        return None
    return parser(raw)


def parse_incidents(
    raw_incidents: list[dict[str, Any]],
    *,
    skip_unknown: bool = True,
) -> list[ParsedIncident]:
    """Parse a list of raw incidents into typed dicts.

    Each incident is dispatched to the correct per-type parser based on
    `incidentType`. Unknown types are filtered out by default (with a
    warning). Set `skip_unknown=False` to keep them as plain dicts.
    """
    results: list[ParsedIncident] = []
    for raw in raw_incidents:
        parsed = parse_incident(raw)
        if parsed is not None:
            results.append(parsed)
        elif not skip_unknown:
            results.append(raw)  # type: ignore[arg-type]
    return results


# =====================================================================
# Periods parser
# =====================================================================

def parse_periods(raw_event: dict[str, Any]) -> ParsedPeriods | None:
    """Reconstruct the period structure from scattered score/time keys
    in a raw event dict.

    This is the most complex parser — it handles:
      - Normal periods (period1, period2, ...)
      - Tiebreak periods (tennis: period1TieBreak, ...)
      - Overtime (football, basketball: overtime)
      - Penalty shootouts (football: penalties)

    Returns None if `defaultPeriodCount` is missing (meaning the event
    doesn't have period structure, e.g. MMA single-round fights).

    REMARK: This function is ported from the original Periods._from_api(),
    which is the single most valuable piece of logic in the old model layer.
    """
    if "defaultPeriodCount" not in raw_event:
        logger.warning(f"Event {raw_event.get('id')} does not have defaultPeriodCount.")
        return None

    home_score: dict = raw_event.get("homeScore", {})
    away_score: dict = raw_event.get("awayScore", {})
    time_info: dict = raw_event.get("time", {})
    period_labels: dict = raw_event.get("periods", {})

    default_count: int = raw_event["defaultPeriodCount"]
    default_period_time: int | None = raw_event.get("defaultPeriodLength")
    default_overtime_time: int | None = raw_event.get("defaultOvertimeLength")

    periods: list[ParsedPeriod] = []

    # --- Normal periods ---
    for k in range(1, default_count + 1):
        key = f"period{k}"
        score: ParsedScore | None = None
        if key in home_score and key in away_score:
            score = ParsedScore(home=home_score[key], away=away_score[key])

        extra_time_val = time_info.get(f"injuryTime{k}")

        periods.append(ParsedPeriod(
            key=key,
            type="normal",
            label=period_labels.get(key),
            score=score,
            time=time_info.get(key),
            defaultTime=default_period_time,
            extraTime=[extra_time_val] if extra_time_val else None,
        ))

    # --- Tiebreak periods (tennis) ---
    for k in range(1, default_count + 1):
        key = f"period{k}TieBreak"
        if key in home_score and key in away_score:
            score = ParsedScore(home=home_score[key], away=away_score[key])
            # Build label: use explicit label, or append " Tie-Break" to parent period label
            label = period_labels.get(key)
            if not label:
                parent_label = period_labels.get(f"period{k}")
                label = f"{parent_label} Tie-Break" if parent_label else None
            periods.append(ParsedPeriod(
                key=key,
                type="tiebreak",
                label=label,
                score=score,
            ))

    # --- Overtime ---
    if "overtime" in home_score and "overtime" in away_score:
        score = ParsedScore(home=home_score["overtime"], away=away_score["overtime"])

        # Collect injury times for overtime periods
        # (injury time indices > defaultPeriodCount belong to overtime)
        extra_time_list: list[int] = []
        for time_key, value in time_info.items():
            if time_key.startswith("injuryTime"):
                try:
                    idx = int(time_key.removeprefix("injuryTime"))
                except ValueError:
                    continue
                if idx > default_count:
                    extra_time_list.append(value)

        periods.append(ParsedPeriod(
            key="overtime",
            type="overtime",
            label=period_labels.get("overtime", "Overtime"),
            score=score,
            defaultTime=default_overtime_time,
            extraTime=extra_time_list if extra_time_list else None,
        ))

    # --- Penalty shootout ---
    if "penalties" in home_score and "penalties" in away_score:
        score = ParsedScore(home=home_score["penalties"], away=away_score["penalties"])
        periods.append(ParsedPeriod(
            key="penalties",
            type="penalties",
            label=period_labels.get("penalties", "Penalty Shootout"),
            score=score,
        ))

    return ParsedPeriods(
        defaultCount=default_count,
        periods=periods,
    )


# =====================================================================
# Statistics helpers
# =====================================================================

def get_statistics_winner(compare_code: int | None) -> str:
    """Map the `compareCode` in a StatisticsItem to a readable string."""
    return WINNER_MAPPING.get(compare_code, "tied")
