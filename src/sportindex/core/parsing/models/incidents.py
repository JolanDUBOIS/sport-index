from __future__ import annotations

from typing import Any, TypedDict, TYPE_CHECKING

from . import logger
from .common import ParsedScore
from ..registry import register

if TYPE_CHECKING:
    from sportindex.core.provider.models import RawIncident


# ======================================================================
# Incidents Parsers
# ======================================================================

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


@register(RawIncident, priority=10)
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


# ======================================================================
# Incidents Parse Types
# ======================================================================

class ParsedGoalIncident(TypedDict, total=False):
    incidentType: str          # always "goal"
    id: int
    time: int
    side: str | None           # "home" / "away"
    score: ParsedScore | None  # running score at time of goal
    scorer: dict               # raw player dict — kept as-is for the higher layer
    assist: dict | None        # raw player dict
    extraTime: int | None      # stoppage-time minute offset
    kind: str | None           # "regular", "ownGoal", "penalty" (football); "try", "twoPoints"... (rugby)


class ParsedPenaltyIncident(TypedDict, total=False):
    """A missed in-play penalty (scored penalties come as GoalIncident)."""
    incidentType: str          # always "penalty"
    id: int
    time: int
    side: str | None
    shooter: dict              # raw player dict
    extraTime: int | None
    description: str | None
    kind: str | None           # "missed", etc.


class ParsedPenaltyShootoutIncident(TypedDict, total=False):
    incidentType: str          # always "penaltyShootout"
    id: int
    side: str | None
    score: ParsedScore | None  # running shootout score
    shooter: dict              # raw player dict
    kind: str | None           # "scored", "missed"


class ParsedCardIncident(TypedDict, total=False):
    incidentType: str          # always "card"
    id: int
    time: int                  # -5 means card given on bench
    side: str | None
    recipient: dict            # raw player OR manager dict
    recipientType: str         # "player" or "manager" — tells you which dict shape it is
    rescinded: bool
    reason: str | None
    extraTime: int | None
    kind: str | None           # "yellow", "red", "yellowRed"


class ParsedPeriodIncident(TypedDict, total=False):
    incidentType: str          # always "period"
    time: int | None           # API sends 999 for "no time" → normalised to None
    score: ParsedScore | None
    kind: str | None           # "HT", "FT", "PEN", etc.


class ParsedVarDecisionIncident(TypedDict, total=False):
    incidentType: str          # always "varDecision"
    id: int
    time: int
    side: str | None
    extraTime: int | None
    description: str | None
    kind: str | None           # "goalAwarded", "penaltyCheck", etc.
    confirmed: bool | None


class ParsedSubstitutionIncident(TypedDict, total=False):
    incidentType: str          # always "substitution"
    id: int
    time: int
    side: str | None
    playerIn: dict             # raw player dict
    playerOut: dict            # raw player dict
    extraTime: int | None
    kind: str | None           # "regular", "injury"


class ParsedExtraTimeIncident(TypedDict, total=False):
    """Injury/added time announcement (not a substitution or event)."""
    incidentType: str          # always "injuryTime"
    time: int
    addedTime: int             # minutes of added time


# Union of all parsed incident types — for type annotations
ParsedIncident = (
    ParsedGoalIncident
    | ParsedPenaltyIncident
    | ParsedPenaltyShootoutIncident
    | ParsedCardIncident
    | ParsedPeriodIncident
    | ParsedVarDecisionIncident
    | ParsedSubstitutionIncident
    | ParsedExtraTimeIncident
)
