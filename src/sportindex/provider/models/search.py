from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar
from pydantic import model_validator

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

T = TypeVar("T", bound=BaseSchema)

class _SearchResultData(BaseSchema, Generic[T]):
    type: str
    score: float
    entity: AnyEntity

    @model_validator(mode='after')
    def validate_entity_type(self) -> _SearchResultData:
        model_cls = ENTITY_MAP.get(self.type)
        
        if not model_cls:
            raise ValueError(f"Unsupported entity type: {self.type}")

        if isinstance(self.entity, dict):
            self.entity = model_cls.model_validate(self.entity)
            
        return self
