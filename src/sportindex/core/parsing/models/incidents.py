"""
NOTE - This might be incomplete, this is based mostly on football events, if the user finds other types of incidents in other sports, they should add them here and update the parser accordingly.
"""

from __future__ import annotations

from typing import Any

from .common import ParsedScore
from sportindex.core.base import BaseModel
from sportindex.core.provider.models import RawPlayer, RawManager


class ParsedGoalIncident(BaseModel):
    incidentType: str          # always "goal"
    id: int
    time: int
    side: str                  # "home" / "away"
    score: ParsedScore         # running score at time of goal
    scorer: RawPlayer          # raw player object
    assist: RawPlayer          # raw player object
    extraTime: int             # stoppage-time minute offset
    kind: str                  # "regular", "ownGoal", "penalty" (football); "try", "twoPoints"... (rugby)


class ParsedPenaltyIncident(BaseModel):
    """A missed in-play penalty (scored penalties come as GoalIncident)."""
    incidentType: str          # always "penalty"
    id: int
    time: int
    side: str                  # "home" / "away"
    shooter: RawPlayer         # raw player object
    extraTime: int
    description: str
    kind: str                  # "missed", etc.


class ParsedPenaltyShootoutIncident(BaseModel):
    incidentType: str          # always "penaltyShootout"
    id: int
    side: str
    score: ParsedScore         # running shootout score
    shooter: RawPlayer         # raw player object
    kind: str                  # "scored", "missed"


class ParsedCardIncident(BaseModel):
    incidentType: str                 # always "card"
    id: int
    time: int                         # -5 means card given on bench
    side: str
    recipient: RawPlayer | RawManager # raw player OR manager object
    recipientType: str                # "player" or "manager" — tells you which dict shape it is
    rescinded: bool
    reason: str
    extraTime: int
    kind: str                         # "yellow", "red", "yellowRed"

    def __init__(self, **data: Any):
        super().__init__(**data)

        # Post-processing to convert recipient dict to RawPlayer or RawManager based on recipientType
        if isinstance(self.recipient, dict):
            if self.recipientType == "player":
                self.recipient = RawPlayer(**self.recipient)
            elif self.recipientType == "manager":
                self.recipient = RawManager(**self.recipient)
            else:
                raise ValueError(f"Unknown recipientType: {self.recipientType}")


class ParsedPeriodIncident(BaseModel):
    incidentType: str          # always "period"
    time: int                  # API sends 999 for "no time" → normalised to None
    score: ParsedScore
    kind: str                  # "HT", "FT", "PEN", etc.


class ParsedVarDecisionIncident(BaseModel):
    incidentType: str          # always "varDecision"
    id: int
    time: int
    side: str
    extraTime: int
    description: str
    kind: str                  # "goalAwarded", "penaltyCheck", etc.
    confirmed: bool


class ParsedSubstitutionIncident(BaseModel):
    incidentType: str          # always "substitution"
    id: int
    time: int
    side: str
    playerIn: RawPlayer        # raw player object
    playerOut: RawPlayer       # raw player object
    extraTime: int
    kind: str                  # "regular", "injury"


class ParsedExtraTimeIncident(BaseModel):
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
