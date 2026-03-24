from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import BaseParsedModel
if TYPE_CHECKING:
    from .core import ParsedCountry
    from .team import ParsedTeam
    from sportindex.provider.raw.models import RawCity, RawCoordinates, RawStadium, RawVenue


@dataclass
class ParsedVenue(BaseParsedModel):
    id: int
    slug: str
    name: str
    capacity: int
    city: RawCity
    stadium: RawStadium
    country: ParsedCountry
    venueCoordinates: RawCoordinates
    mainTeams: list[ParsedTeam]

    @classmethod
    def _parse(cls, raw: RawVenue) -> ParsedVenue:
        from .core import ParsedCountry
        from .team import ParsedTeam
        return cls(
            id = raw.get("id"),
            slug = raw.get("slug"),
            name = raw.get("name"),
            capacity = raw.get("capacity"),
            city = raw.get("city"),
            stadium = raw.get("stadium"),
            country = ParsedCountry.from_raw(raw.get("country")),
            venueCoordinates = raw.get("venueCoordinates"),
            mainTeams = [ParsedTeam.from_raw(t) for t in raw.get("mainTeams", [])],
        )
