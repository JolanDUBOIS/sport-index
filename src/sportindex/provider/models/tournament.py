from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import Field

from .base import BaseSchema

if TYPE_CHECKING:
    from .core import _SportData, _CountryData, _CategoryData
    from .manager import _ManagerData
    from .primitives import Amount
    from .team import _TeamData
    from .venue import _VenueData


# ===========================================================================
# Season
# ===========================================================================

class _SeasonData(BaseSchema):
    id: int
    name: str
    year: str | None = None              # e.g. "24/25" or "2025"
    description: str | None = None
    start: datetime | None = Field(default=None, alias="startDateTimestamp")


# ===========================================================================
# Unique Tournament
# ===========================================================================

class _UniqueTournamentData(BaseSchema):
    id: int
    slug: str
    name: str
    category: _CategoryData
    gender: str | None = None
    tier: int | None = None
    title_holder_titles: int | None = None
    most_titles: int | None = None
    has_rounds: bool | None = None
    has_groups: bool | None = None
    has_playoff_series: bool | None = None
    ground_type: str | None = None         # e.g. "Red clay", "Grass", etc.
    number_of_sets: int | None = None
    tennis_points: int | None = None
    start: datetime | None = Field(default=None, alias="startDateTimestamp")
    end: datetime | None = Field(default=None, alias="endDateTimestamp")
    upper_divisions: list[_UniqueTournamentData] = Field(default_factory=list)
    lower_divisions: list[_UniqueTournamentData] = Field(default_factory=list)
    title_holder: _TeamData | None = None
    most_titles_teams: list[_TeamData] = Field(default_factory=list)
    linked_unique_tournaments: list[_UniqueTournamentData] = Field(default_factory=list)
    

# ===========================================================================
# Tournament
# ===========================================================================

class _TournamentData(BaseSchema):
    id: int
    slug: str
    name: str
    category: _CategoryData | None = None
    unique_tournament: _UniqueTournamentData | None = None
