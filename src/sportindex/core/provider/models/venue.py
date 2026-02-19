from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .core import BaseModel, Country
from .participants import Team


@dataclass(frozen=True, kw_only=True)
class Coordinates(BaseModel):
    latitude: float
    longitude: float

    @classmethod
    def _from_api(cls, raw: dict) -> Coordinates:
        return Coordinates(
            latitude=raw.get("latitude"),
            longitude=raw.get("longitude"),
        )

@dataclass(frozen=True, kw_only=True)
class Stadium(BaseModel):
    name: str
    capacity: int

    @classmethod
    def _from_api(cls, raw: dict) -> Stadium:
        return Stadium(
            name=raw.get("name"),
            capacity=raw.get("capacity"),
        )

@dataclass(frozen=True, kw_only=True)
class Venue(BaseModel):
    id: str
    slug: str
    name: str
    capacity: int
    city: str
    stadium: Stadium
    country: Country
    coordinates: Coordinates
    main_teams: Optional[list[Team]] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Venue:
        return Venue(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            capacity=raw.get("capacity"),
            city=raw.get("city"),
            stadium=Stadium.from_api(raw.get("stadium")),
            country=Country.from_api(raw.get("country")),
            coordinates=Coordinates.from_api(raw.get("coordinates")),
            main_teams=[Team.from_api(t) for t in raw.get("mainTeams", [])] if raw.get("mainTeams") else None,
        )
    # NOTE - To be verified, not sure for stadium...
