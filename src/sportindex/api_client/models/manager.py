from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING, Literal

from pydantic import Field

from .base import BaseSchema

if TYPE_CHECKING:
    from .core import _CountryData, _SportData
    from .primitives import Performance
    from .team import _TeamData


class _ManagerData(BaseSchema):
    id: int
    slug: str
    name: str
    short_name: str | None = None
    sport: _SportData | None = None
    country: _CountryData | None = None
    nationality: str | None = None             # ISO3
    nationalityISO2: str | None = None         # ISO2  # noqa: N815
    deceased: bool | None = None
    performance: Performance | None = None
    preferred_formation: str | None = None      # e.g. "4-3-3"
    former_player_id: int | None = None
    team: _TeamData | None = None
    teams: list[_TeamData] = Field(default_factory=list)
    date_of_birth: datetime | None = Field(default=None, alias="dateOfBirthTimestamp")
    role: Literal["manager"] = Field(default="manager")


class ManagerTenure(BaseSchema):
    performance: Performance
    team: _TeamData
    start: datetime | None = Field(default=None, alias="startTimestamp")
    end: datetime | None = Field(default=None, alias="endTimestamp")
