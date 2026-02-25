from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING

from . import logger
from .common import ParsedScore
from ..registry import register

if TYPE_CHECKING:
    from sportindex.core.provider.models import (
        RawEvent, RawRound, RawSeason,
        RawTournament,
        RawReferee, RawTeam, RawVenue,
        RawStatus, Timestamp
    )


# =====================================================================
# Parsers
# =====================================================================

@register(RawEvent, priority=10)
def parse_event(raw_event: RawEvent) -> ParsedEvent:
    """
    Parse a RawEvent into a ParsedEvent.
    - Applies parse_periods on raw_event
    - Removes homeScore, awayScore, time, periods, team and sport-specific fields from raw_event
    - Adds parsed periods to the output dict as 'parsedPeriods'
    - Groups team fields under 'home' and 'away'
    - Adds 'extra' field for sport-specific details (fight or racket)
    """
    event = dict(raw_event)
    for key in (
        "homeScore", "awayScore", "time", "periods",
        "defaultPeriodCount", "defaultPeriodLength", "defaultOvertimeLength",
        "homeTeam", "homeTeamSeed", "homeTeamRanking",
        "awayTeam", "awayTeamSeed", "awayTeamRanking",
        "fightType", "weightClass", "winType", "finalRound", "firstToServe"
    ):
        event.pop(key, None)

    # Teams
    event["home"] = parse_team(raw_event, "home")
    event["away"] = parse_team(raw_event, "away")

    # Extra (sport-specific)
    extra = parse_extra(raw_event)
    if extra is not None:
        event["extra"] = extra

    # Periods
    parsed_periods = parse_periods(raw_event)
    if parsed_periods is not None:
        event["parsedPeriods"] = parsed_periods
    return event


def parse_team(raw_event: RawEvent, side: str) -> ParsedTeam:
    """Parse team info for 'home' or 'away'."""
    return {
        "team": raw_event.get(f"{side}Team"),
        "seed": raw_event.get(f"{side}TeamSeed"),
        "ranking": raw_event.get(f"{side}TeamRanking"),
        "score": raw_event.get(f"{side}Score", {}).get("display"),
    }


def parse_extra(raw_event: RawEvent) -> ParsedExtra | None:
    """Parse sport-specific extra info (fight or racket)."""
    # Fight sports
    if any(raw_event.get(k) is not None for k in ("fightType", "weightClass", "winType", "finalRound")):
        extra: ParsedFightExtra = {}
        if raw_event.get("fightType") is not None:
            extra["fightType"] = raw_event["fightType"]
        if raw_event.get("weightClass") is not None:
            extra["weightClass"] = raw_event["weightClass"]
        if raw_event.get("winType") is not None:
            extra["winType"] = raw_event["winType"]
        if raw_event.get("finalRound") is not None:
            extra["finalRound"] = raw_event["finalRound"]
        return extra if extra else None
    # Racket sports
    if raw_event.get("firstToServe") is not None:
        return {"firstToServe": raw_event["firstToServe"]}
    return None


def parse_periods(raw_event: RawEvent) -> ParsedPeriods | None:
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
# Parsed Types
# =====================================================================

class ParsedEvent(TypedDict, total=False):
    id: int
    customId: str
    slug: str
    startTimestamp: Timestamp
    gender: str
    season: RawSeason
    tournament: RawTournament
    roundInfo: RawRound
    previousLegEventId: int

    referee: RawReferee
    venue: RawVenue
    attendance: int

    status: RawStatus
    winnerCode: int

    # Grouped fields
    home: ParsedTeam
    away: ParsedTeam
    extra: ParsedExtra  # Optional, only present if relevant

    # Parsed periods
    parsedPeriods: ParsedPeriods


class ParsedTeam(TypedDict, total=False):
    team: RawTeam
    seed: int
    ranking: int
    score: int


class ParsedFightExtra(TypedDict, total=False):
    fightType: str
    weightClass: str
    winType: str
    finalRound: int
    order: list[int]

class ParsedRacketExtra(TypedDict, total=False):
    firstToServe: int

ParsedExtra = ParsedFightExtra | ParsedRacketExtra


class ParsedPeriod(TypedDict, total=False):
    """A single period as reconstructed by parse_periods().
    The key/type pair uniquely identifies the period.
    """
    key: str               # e.g. "period1", "overtime", "penalties", "period2TieBreak"
    type: str              # "normal", "overtime", "tiebreak", "penalties"
    label: str | None      # Display label, e.g. "1st Half", "Overtime"
    score: ParsedScore | None
    time: int | None       # Actual elapsed time for this period (if known)
    defaultTime: int | None
    extraTime: list[int] | None  # Injury/stoppage time added in this period

class ParsedPeriods(TypedDict):
    """Output of parse_periods(). Reconstructs period structure from the
    scattered score/time keys in a raw event dict."""
    defaultCount: int
    periods: list[ParsedPeriod]
