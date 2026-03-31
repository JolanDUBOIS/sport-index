from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import Field

from .base import BaseSchema

if TYPE_CHECKING:
    from .core import _CountryData, _CategoryData
    from .primitives import EventStatus
    from .team import _TeamData


# ===========================================================================
# Primitives
# ===========================================================================

class _StageTypeData(BaseSchema):
    id: int
    name: str  # "Season", "Event", or other values


class _StageInfoData(BaseSchema):
    stage_type: str | None = None     # e.g. "flat", "mountain", etc.
    stage_round: int | None = None
    discipline: str | None = None
    circuit: str | None = None       # Circuit name
    circuit_city: str | None = None
    circuit_country: str | None = None
    circuit_length: float | None = None  # In meters
    track_condition: str | None = None
    weather: str | None = None
    air_temperature: float | None = None
    track_temperature: float | None = None
    humidity: float | None = None
    race_type: str | None = None      # e.g. "normal", "timetrial"
    laps: int | None = None
    race_distance: int | None = None   # In meters
    laps_completed: int | None = None
    lap_record: str | None = None
    departure_city: str | None = None  # Cycling stages
    arrival_city: str | None = None


class _StageParentData(BaseSchema):
    id: int
    slug: str
    description: str
    start: datetime | None = Field(default=None, alias="startDateTimestamp")


# ===========================================================================
# Unique Stage
# ===========================================================================

class _UniqueStageData(BaseSchema):
    id: int
    slug: str
    name: str
    category: _CategoryData
    description: str | None = None


# ===========================================================================
# Stage
# ===========================================================================

class _StageData(BaseSchema):
    id: int
    slug: str
    name: str
    description: str | None = None
    year: str | None = None
    season_stage_name: str | None = None
    unique_stage: _UniqueStageData
    type_: _StageTypeData | None = Field(default=None, alias="type")
    status: EventStatus | None = None
    flag: str | None = None
    country: _CountryData | None = None
    info: _StageInfoData | None = None
    start: datetime | None = Field(default=None, alias="startDateTimestamp")
    end: datetime | None = Field(default=None, alias="endDateTimestamp")
    parent: _StageParentData | None = Field(default=None, alias="stageParent")
    winner: _TeamData | None = None
    substages: list[_StageData] = Field(default_factory=list)
