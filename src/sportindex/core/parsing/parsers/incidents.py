"""
NOTE - This might be incomplete, this is based mostly on football events, if the user finds other types of incidents in other sports, they should add them here and update the parser accordingly.
"""

from __future__ import annotations

from typing import Any

from . import logger
from ..models import (
    ParsedScore, ParsedGoalIncident,
    ParsedPenaltyIncident, ParsedPenaltyShootoutIncident,
    ParsedCardIncident, ParsedPeriodIncident,
    ParsedVarDecisionIncident, ParsedSubstitutionIncident,
    ParsedExtraTimeIncident, ParsedIncident
)
from ..registry import register
from sportindex.core.provider.models import RawIncident


# ======================================================================
# Incidents Parsers
# ======================================================================

def _get_side(raw: RawIncident) -> str:
    """Convert `isHome` boolean to "home" / "away" / None."""
    if "isHome" not in raw:
        return None
    return "home" if raw["isHome"] else "away"


def _get_score(raw: RawIncident) -> ParsedScore:
    """Extract running score from an incident (flat homeScore/awayScore ints)."""
    if "homeScore" in raw and "awayScore" in raw:
        return ParsedScore(home=raw["homeScore"], away=raw["awayScore"])
    return None


# -- Per-type parsers --------------------------------------------------

def _parse_goal(raw: RawIncident) -> ParsedGoalIncident:
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


def _parse_penalty(raw: RawIncident) -> ParsedPenaltyIncident:
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


def _parse_penalty_shootout(raw: RawIncident) -> ParsedPenaltyShootoutIncident:
    return ParsedPenaltyShootoutIncident(
        incidentType="penaltyShootout",
        id=raw.get("id"),
        side=_get_side(raw),
        score=_get_score(raw),
        shooter=raw.get("player"),
        kind=raw.get("incidentClass"),    # "scored", "missed"
    )


def _parse_card(raw: RawIncident) -> ParsedCardIncident:
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


def _parse_period(raw: RawIncident) -> ParsedPeriodIncident:
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


def _parse_var_decision(raw: RawIncident) -> ParsedVarDecisionIncident:
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


def _parse_substitution(raw: RawIncident) -> ParsedSubstitutionIncident:
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


def _parse_extra_time(raw: RawIncident) -> ParsedExtraTimeIncident:
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


@register(RawIncident)
def parse_incident(raw: RawIncident) -> ParsedIncident:
    """Parse a single raw incident into a typed dict.

    Returns None if the incident type is unknown (and logs a warning).
    """
    if not isinstance(raw, RawIncident):
        raise ValueError(f"Expected RawIncident, got {type(raw)}")
    parser = _INCIDENT_PARSERS.get(raw.incidentType)
    if parser is None:
        logger.warning(
            f"Unknown incident type '{raw.incidentType}' — skipping. "
            f"Add a parser to _INCIDENT_PARSERS if it should be handled."
        )
        return None
    return parser(raw)
