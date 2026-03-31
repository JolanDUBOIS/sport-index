from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

from .base import BaseSchema

if TYPE_CHECKING:
    from .core import _CountryData
    from .team import _TeamData


class _CoordinatesData(BaseSchema):
    latitude: float
    longitude: float


class _CityData(BaseSchema):
    name: str


class _StadiumData(BaseSchema):
    name: str
    capacity: int | None = None


class _VenueData(BaseSchema):
    id: int
    slug: str
    name: str
    capacity: int | None = None
    city: _CityData | None = None
    stadium: _StadiumData | None = None
    country: _CountryData | None = None
    coordinates: _CoordinatesData = Field(default=None, alias="venueCoordinates")
    main_teams: list[_TeamData] = Field(default_factory=list)


class VenueStatistics(BaseSchema):
    total_matches: int
    home_team_goals_scored: int
    away_team_goals_scored: int
    avg_red_cards_per_game: float
    avg_corner_kicks_per_game: float
    home_team_wins_percentage: float
    away_team_wins_percentage: float
    draws_percentage: float
