from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING

from pydantic import Field

from .base import BaseSchema

if TYPE_CHECKING:
    from .stage import _StageData
    from .team import _TeamData


class RaceResults(BaseSchema):
    position: int | None = None
    points: int | None = None
    time: str | None = None                      # Finishing time
    stage: _StageData | None = None
    grid_position: int | None = None
    gap: str | None = None         # Gap to leader
    updated_at: datetime | None = Field(default=None, alias="updatedAtTimestamp")


class SeasonCareerHistory(BaseSchema):
    position: int
    points: int
    victories: int
    podiums: int
    pole_positions: int
    races_started: int
    stage: _StageData | None = None
    parent_team: _TeamData | None = None
    updated_at: datetime | None = Field(default=None, alias="updatedAtTimestamp")


class TotalCareerHistory(BaseSchema):
    team: _TeamData
    world_championships_titles: int
    victories: int
    podiums: int | None = None
    pole_positions: int | None = None
    races_started: int | None = None


class DriverCareerHistory(BaseSchema):
    total: TotalCareerHistory
    seasons: list[SeasonCareerHistory] = Field(default_factory=list, alias="bySeason")


class Lap(BaseSchema):
    lap: int
    position: int
    tyre_type: str
    visited_pit_stop: bool = Field(default=False)


class DriverPerformance(BaseSchema):
    id: int
    name: str
    slug: str
    start_number: int
    laps: list[Lap] = Field(default_factory=list)
    parent_team: _TeamData | None = None
