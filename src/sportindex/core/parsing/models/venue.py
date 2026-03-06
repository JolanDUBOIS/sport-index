from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .team import ParsedTeam
    from sportindex.core.provider.models import City, Country, Coordinates, Stadium, Venue


@dataclass
class ParsedVenue:
    id: int
    slug: str
    name: str
    capacity: int
    city: City
    stadium: Stadium
    country: Country
    venueCoordinates: Coordinates
    mainTeams: list[ParsedTeam]

    @classmethod
    def from_raw(cls, raw: Venue) -> ParsedVenue:
        from .team import ParsedTeam
        return cls(
            id = raw.get("id"),
            slug = raw.get("slug"),
            name = raw.get("name"),
            capacity = raw.get("capacity"),
            city = raw.get("city"),
            stadium = raw.get("stadium"),
            country = raw.get("country"),
            venueCoordinates = raw.get("venueCoordinates"),
            mainTeams = [ParsedTeam.from_raw(t) for t in raw.get("mainTeams", [])],
        )
