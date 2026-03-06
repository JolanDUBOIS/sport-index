from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from .base import BaseParsedModel
from .parsers import parse_timestamp
if TYPE_CHECKING:
    from sportindex.core.provider.models import Referee, Sport, Country


@dataclass
class ParsedReferee(BaseParsedModel):
    id: int
    slug: str
    name: str
    games: int
    sport: Sport
    country: Country
    yellowCards: int
    redCards: int
    yellowRedCards: int
    dateOfBirthTimestamp: datetime

    @classmethod
    def _parse(cls, raw: Referee) -> ParsedReferee:
        return cls(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            games=raw.get("games"),
            sport=raw.get("sport"),
            country=raw.get("country"),
            yellowCards=raw.get("yellowCards"),
            redCards=raw.get("redCards"),
            yellowRedCards=raw.get("yellowRedCards"),
            dateOfBirthTimestamp=parse_timestamp(raw.get("dateOfBirthTimestamp"))
        )
