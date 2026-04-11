from __future__ import annotations

from typing import Generic, TypeVar, Any
from pydantic import model_validator

from . import logger
from .base import BaseSchema
from .manager import _ManagerData
from .player import _PlayerData
from .referee import _RefereeData
from .team import _TeamData
from .tournament import _UniqueTournamentData
from .stage import _UniqueStageData, _StageData
from .venue import _VenueData


AnyEntity = (
    _ManagerData
    | _PlayerData
    | _RefereeData
    | _TeamData
    | _UniqueTournamentData
    | _UniqueStageData
    | _StageData
    | _VenueData
)

ENTITY_MAP: dict[str, type[BaseSchema]] = {
    "manager": _ManagerData,
    "player": _PlayerData,
    "referee": _RefereeData,
    "team": _TeamData,
    "uniqueTournament": _UniqueTournamentData,
    "uniqueStage": _UniqueStageData,
    "stage": _StageData,
    "venue": _VenueData,
}

T = TypeVar("T", bound="BaseSchema")

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
