from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from .base import BaseParsedModel
from .parsers import parse_timestamp
if TYPE_CHECKING:
    from .core import ParsedSport, ParsedCountry
    from sportindex.provider.raw import RawReferee


@dataclass
class ParsedReferee(BaseParsedModel):
    id: int
    slug: str
    name: str
    games: int
    sport: ParsedSport
    country: ParsedCountry
    yellowCards: int
    redCards: int
    yellowRedCards: int
    dateOfBirth: datetime

    @classmethod
    def _parse(cls, raw: RawReferee) -> ParsedReferee:
        from .core import ParsedSport, ParsedCountry
        return cls(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            games=raw.get("games"),
            sport=ParsedSport.from_raw(raw.get("sport")),
            country=ParsedCountry.from_raw(raw.get("country")),
            yellowCards=raw.get("yellowCards"),
            redCards=raw.get("redCards"),
            yellowRedCards=raw.get("yellowRedCards"),
            dateOfBirth=parse_timestamp(raw.get("dateOfBirthTimestamp"))
        )
