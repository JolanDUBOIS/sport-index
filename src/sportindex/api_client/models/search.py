from __future__ import annotations

from typing import Any, Generic

from pydantic import model_validator
from typing_extensions import TypeVar

from .base import BaseSchema
from .event import _EventData
from .manager import _ManagerData
from .player import _PlayerData
from .referee import _RefereeData
from .stage import _StageData, _UniqueStageData
from .team import _TeamData
from .tournament import _UniqueTournamentData
from .venue import _VenueData

AnyEntity = (
    _EventData
    | _ManagerData
    | _PlayerData
    | _RefereeData
    | _TeamData
    | _UniqueTournamentData
    | _UniqueStageData
    | _StageData
    | _VenueData
)

ENTITY_MAP: dict[str, type[BaseSchema]] = {
    "event": _EventData,
    "manager": _ManagerData,
    "player": _PlayerData,
    "referee": _RefereeData,
    "team": _TeamData,
    "uniqueTournament": _UniqueTournamentData,
    "uniqueStage": _UniqueStageData,
    "stage": _StageData,
    "venue": _VenueData,
}

T = TypeVar("T", bound="BaseSchema", default="BaseSchema")

class _SearchResultData(BaseSchema, Generic[T]):
    type: str
    score: float
    entity: AnyEntity

    @model_validator(mode="before")
    @classmethod
    def validate_entity_mapping(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        entity_type = data.get("type")
        entity_data = data.get("entity")

        if entity_type not in ENTITY_MAP:
            raise ValueError(f"Unsupported entity type: {entity_type}")

        model_cls = ENTITY_MAP[entity_type]

        if isinstance(entity_data, dict):
            data["entity"] = model_cls.model_validate(entity_data)

        return data
