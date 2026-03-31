from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Annotated, Union

from pydantic import Field, ValidationInfo, model_validator

from .base import BaseSchema

if TYPE_CHECKING:
    from .manager import _ManagerData
    from .primitives import Score
    from .player import _PlayerData


# =====================================================================
# Base Incident Class
# =====================================================================

class _BaseIncident(BaseSchema):

    @model_validator(mode='before')
    @classmethod
    def reshape_common_incident_fields(cls, data: Any, info: ValidationInfo) -> Any:
        if not isinstance(data, dict):
            return data

        if info.context and info.context.get("preprocessed"):
            return data

        # 1. Side logic
        if "isHome" in data:
            data["side"] = "home" if data["isHome"] else "away"

        # 2. Score logic
        if "homeScore" in data and "awayScore" in data:
            data["score"] = {"home": data["homeScore"], "away": data["awayScore"]}

        # 3. Time logic
        if data.get("time") == 999:
            data["time"] = -1  # Normalise "no time" to -1 for easier handling in code

        return data


# =====================================================================
# Specific Incident Types
# =====================================================================

class GoalIncident(_BaseIncident):
    incident_type: Literal["goal"]
    id: int
    time: int
    side: str                                 # "home" / "away"
    score: Score                              # running score at time of goal
    scorer: _PlayerData = Field(alias="player")
    assist: _PlayerData | None = None
    extra_time: int | None = Field(default=None, alias="addedTime")
    kind: str = Field(alias="incidentClass")  # "regular", "ownGoal", "penalty" (football); "try", "twoPoints"... (rugby)


class PenaltyIncident(_BaseIncident):
    incident_type: Literal["penalty"]
    id: int
    time: int
    side: str                                 # "home" / "away"
    shooter: _PlayerData = Field(alias="player")
    extra_time: int | None = Field(default=None, alias="addedTime")
    description: str | None = None
    kind: str = Field(alias="incidentClass")  # "missed", etc.


class PenaltyShootoutIncident(_BaseIncident):
    incident_type: Literal["penaltyShootout"]
    id: int
    side: str
    score: Score                              # running shootout score
    shooter: _PlayerData = Field(alias="player")
    kind: str = Field(alias="incidentClass")  # "scored", "missed"


class CardIncident(_BaseIncident):
    incident_type: Literal["card"]
    id: int
    time: int                                 # -5 means card given on bench
    side: str
    recipient: Annotated[Union[_PlayerData, _ManagerData], Field(discriminator="role")]
    rescinded: bool = Field(default=False)
    reason: str | None = None
    extra_time: int | None = Field(default=None, alias="addedTime")
    kind: str = Field(alias="incidentClass")  # "yellow", "red", "yellowRed"

    @model_validator(mode='before')
    @classmethod
    def set_recipient(cls, data: Any, info: ValidationInfo) -> Any:
        if not isinstance(data, dict):
            return data

        if info.context and info.context.get("preprocessed"):
            return data

        if data.get("player"):
            recipient_dict = data["player"]
            recipient_dict["role"] = "player"
            data["recipient"] = recipient_dict
        elif data.get("manager"):
            recipient_dict = data["manager"]
            recipient_dict["role"] = "manager"
            data["recipient"] = recipient_dict

        return data


class PeriodIncident(_BaseIncident):
    incident_type: Literal["period"]
    time: int                                 # API sends 999 for "no time" → normalised to None
    score: Score
    kind: str = Field(alias="text")           # "HT", "FT", "PEN", etc.


class VarDecisionIncident(_BaseIncident):
    incident_type: Literal["varDecision"]
    id: int
    time: int
    side: str
    confirmed: bool
    description: str | None = Field(default=None, alias="text")
    extra_time: int | None = Field(default=None, alias="addedTime")
    kind: str = Field(alias="incidentClass")  # "goalAwarded", "penaltyCheck", etc.


class SubstitutionIncident(_BaseIncident):
    incident_type: Literal["substitution"]
    id: int
    time: int
    side: str
    player_in: _PlayerData = Field(alias="playerIn")
    player_out: _PlayerData = Field(alias="playerOut")
    extra_time: int | None = Field(default=None, alias="addedTime")
    kind: str = Field(alias="incidentClass")  # "regular", "injury"


class ExtraTimeIncident(_BaseIncident):
    incident_type: Literal["injuryTime"]
    time: int
    added_time: int                           # minutes of added time


# =====================================================================
# Incidents
# =====================================================================

Incident = Annotated[
    GoalIncident
    | PenaltyIncident
    | PenaltyShootoutIncident
    | CardIncident
    | PeriodIncident
    | VarDecisionIncident
    | SubstitutionIncident
    | ExtraTimeIncident,
    Field(discriminator="incident_type")
]