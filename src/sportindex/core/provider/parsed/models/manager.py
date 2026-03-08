from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from .base import BaseParsedModel
from .parsers import parse_timestamp
if TYPE_CHECKING:
    from .core import ParsedSport, ParsedCountry
    from .team import ParsedTeam
    from sportindex.core.provider.raw.models import Manager, Performance


@dataclass
class ParsedManager(BaseParsedModel):
    id: int
    slug: str
    name: str
    shortName: str
    sport: ParsedSport
    country: ParsedCountry
    nationality: str              # ISO3
    nationalityISO2: str          # ISO2
    deceased: bool
    performance: Performance
    preferredFormation: str       # e.g. "4-3-3"
    formerPlayerId: int
    team: ParsedTeam
    teams: list[ParsedTeam]
    dateOfBirthTimestamp: datetime

    @classmethod
    def _parse(cls, raw: Manager) -> ParsedManager:
        from .core import ParsedSport, ParsedCountry
        from .team import ParsedTeam
        return cls(
            id = raw.get("id"),
            slug = raw.get("slug"),
            name = raw.get("name"),
            shortName = raw.get("shortName"),
            sport = ParsedSport.from_raw(raw.get("sport")),
            country = ParsedCountry.from_raw(raw.get("country")),
            nationality = raw.get("nationality"),
            nationalityISO2 = raw.get("nationalityISO2"),
            deceased = raw.get("deceased"),
            performance = raw.get("performance"),
            preferredFormation = raw.get("preferredFormation"),
            formerPlayerId = raw.get("formerPlayerId"),
            team = ParsedTeam.from_raw(raw.get("team")),
            teams = [ParsedTeam.from_raw(t) for t in raw.get("teams", [])],
            dateOfBirthTimestamp = parse_timestamp(raw.get("dateOfBirthTimestamp")),
        )
