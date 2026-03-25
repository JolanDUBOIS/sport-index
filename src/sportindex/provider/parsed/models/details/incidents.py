from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..base import BaseParsedModel

if TYPE_CHECKING:
    from ..manager import ParsedManager
    from ..player import ParsedPlayer
    from ..event import ParsedScore
    from sportindex.provider.raw.models import RawIncident


# =====================================================================
# Parsed Incidents
# =====================================================================

@dataclass
class ParsedIncident(BaseParsedModel):
    incidentType: str

    @classmethod
    def _parse(cls, raw: RawIncident) -> ParsedIncident:
        incident_type = raw.get("incidentType")
        if incident_type in _INCIDENT_TYPE_MAPPING:
            return _INCIDENT_TYPE_MAPPING[incident_type].from_raw(raw)
        else:
            raise ValueError(f"Unknown incident type: {incident_type}")


@dataclass
class ParsedGoalIncident(ParsedIncident):
    id: int
    time: int
    side: str                  # "home" / "away"
    score: ParsedScore         # running score at time of goal
    scorer: ParsedPlayer       # parsed player object
    assist: ParsedPlayer       # parsed player object
    extraTime: int             # stoppage-time minute offset
    kind: str                  # "regular", "ownGoal", "penalty" (football); "try", "twoPoints"... (rugby)

    @classmethod
    def _parse(cls, raw: RawIncident) -> ParsedGoalIncident:
        from ..player import ParsedPlayer
        return cls(
            incidentType="goal",
            id=raw.get("id"),
            time=raw.get("time"),
            side=_get_side(raw),
            score=_get_score(raw),
            scorer=ParsedPlayer.from_raw(raw.get("player")),        # raw player dict, kept as-is
            assist=ParsedPlayer.from_raw(raw.get("assist")),         # raw player dict or None
            extraTime=raw.get("addedTime"),
            kind=raw.get("incidentClass"),    # "regular", "ownGoal", "penalty", "try", "twoPoints"...
        )


@dataclass
class ParsedPenaltyIncident(ParsedIncident):
    """A missed in-play penalty (scored penalties come as GoalIncident)."""
    id: int
    time: int
    side: str                  # "home" / "away"
    shooter: ParsedPlayer      # parsed player object
    extraTime: int
    description: str
    kind: str                  # "missed", etc.

    @classmethod
    def _parse(cls, raw: RawIncident) -> ParsedPenaltyIncident:
        from ..player import ParsedPlayer
        return cls(
            incidentType="penalty",
            id=raw.get("id"),
            time=raw.get("time"),
            side=_get_side(raw),
            shooter=ParsedPlayer.from_raw(raw.get("player")),
            extraTime=raw.get("addedTime"),
            description=raw.get("description"),
            kind=raw.get("incidentClass"),
        )


@dataclass
class ParsedPenaltyShootoutIncident(ParsedIncident):
    id: int
    side: str
    score: ParsedScore         # running shootout score
    shooter: ParsedPlayer      # parsed player object
    kind: str                  # "scored", "missed"

    @classmethod
    def _parse(cls, raw: RawIncident) -> ParsedPenaltyShootoutIncident:
        from ..player import ParsedPlayer
        return cls(
            incidentType="penaltyShootout",
            id=raw.get("id"),
            side=_get_side(raw),
            score=_get_score(raw),
            shooter=ParsedPlayer.from_raw(raw.get("player")),
            kind=raw.get("incidentClass"),    # "scored", "missed"
        )


@dataclass
class ParsedCardIncident(ParsedIncident):
    id: int
    time: int                         # -5 means card given on bench
    side: str
    recipient: ParsedPlayer | ParsedManager
    rescinded: bool
    reason: str
    extraTime: int
    kind: str                         # "yellow", "red", "yellowRed"

    @classmethod
    def _parse(cls, raw: RawIncident) -> ParsedCardIncident:
        if raw.get("player"):
            from ..player import ParsedPlayer
            recipient = ParsedPlayer.from_raw(raw.get("player"))
        else:
            from ..manager import ParsedManager
            recipient = ParsedManager.from_raw(raw.get("manager"))
        
        return cls(
            incidentType="card",
            id=raw.get("id"),
            time=raw.get("time"),             # -5 means card given on bench
            side=_get_side(raw),
            recipient=recipient,
            rescinded=raw.get("rescinded", False),
            reason=raw.get("reason"),
            extraTime=raw.get("addedTime"),
            kind=raw.get("incidentClass"),    # "yellow", "red", "yellowRed"
        )


@dataclass
class ParsedPeriodIncident(ParsedIncident):
    time: int                  # API sends 999 for "no time" → normalised to None
    score: ParsedScore
    kind: str                  # "HT", "FT", "PEN", etc.

    @classmethod
    def _parse(cls, raw: RawIncident) -> ParsedPeriodIncident:
        time = raw.get("time")
        if time == 999:
            time = None

        return cls(
            incidentType="period",
            time=time,
            score=_get_score(raw),
            kind=raw.get("text"),             # "HT", "FT", "PEN", etc.
        )


@dataclass
class ParsedVarDecisionIncident(ParsedIncident):
    id: int
    time: int
    side: str
    extraTime: int
    description: str
    kind: str                  # "goalAwarded", "penaltyCheck", etc.
    confirmed: bool

    @classmethod
    def _parse(cls, raw: RawIncident) -> ParsedVarDecisionIncident:
        return cls(
            incidentType="varDecision",
            id=raw.get("id"),
            time=raw.get("time"),
            side=_get_side(raw),
            extraTime=raw.get("addedTime"),
            description=raw.get("text"),
            kind=raw.get("incidentClass"),    # "goalAwarded", "penaltyCheck", etc.
            confirmed=raw.get("confirmed"),
        )


@dataclass
class ParsedSubstitutionIncident(ParsedIncident):
    id: int
    time: int
    side: str
    playerIn: ParsedPlayer     # parsed player object
    playerOut: ParsedPlayer    # parsed player object
    extraTime: int
    kind: str                  # "regular", "injury"


    @classmethod
    def _parse(cls, raw: RawIncident) -> ParsedSubstitutionIncident:
        from ..player import ParsedPlayer
        return cls(
            incidentType="substitution",
            id=raw.get("id"),
            time=raw.get("time"),
            side=_get_side(raw),
            playerIn=ParsedPlayer.from_raw(raw.get("playerIn")),
            playerOut=ParsedPlayer.from_raw(raw.get("playerOut")),
            extraTime=raw.get("addedTime"),
            kind=raw.get("incidentClass"),    # "regular", "injury"
        )


@dataclass
class ParsedExtraTimeIncident(ParsedIncident):
    """Injury/added time announcement (not a substitution or event)."""
    time: int
    addedTime: int             # minutes of added time

    @classmethod
    def _parse(cls, raw: RawIncident) -> ParsedExtraTimeIncident:
        return cls(
            incidentType="injuryTime",
            time=raw.get("time"),
            addedTime=raw.get("length"),      # minutes of added time
        )


# =====================================================================
# Incident Types Mapping
# =====================================================================

_INCIDENT_TYPE_MAPPING: dict[str, type[ParsedIncident]] = {
    "goal": ParsedGoalIncident,
    "penalty": ParsedPenaltyIncident,
    "penaltyShootout": ParsedPenaltyShootoutIncident,
    "card": ParsedCardIncident,
    "period": ParsedPeriodIncident,
    "varDecision": ParsedVarDecisionIncident,
    "substitution": ParsedSubstitutionIncident,
    "injuryTime": ParsedExtraTimeIncident,
}


# =====================================================================
# Helpers
# =====================================================================

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
