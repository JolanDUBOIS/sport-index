from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import BaseParsedModel
if TYPE_CHECKING:
    from sportindex.provider.raw.models import Sport, Country, Category


@dataclass
class ParsedSport(BaseParsedModel):
    id: int
    name: str
    slug: str

    @classmethod
    def _parse(cls, raw: Sport) -> ParsedSport:
        return cls(
            id = raw.get("id"),
            name = raw.get("name"),
            slug = raw.get("slug"),
        )


@dataclass
class ParsedCountry(BaseParsedModel):
    name: str
    slug: str
    alpha2: str
    alpha3: str
    flag: str

    @classmethod
    def _parse(cls, raw: Country) -> ParsedCountry:
        return cls(
            name = raw.get("name"),
            slug = raw.get("slug"),
            alpha2 = raw.get("alpha2"),
            alpha3 = raw.get("alpha3"),
            flag = raw.get("flag"),
        )


@dataclass
class ParsedCategory(BaseParsedModel):
    id: int
    name: str
    slug: str
    sport: ParsedSport
    alpha2: str
    flag: str
    country: ParsedCountry

    @classmethod
    def _parse(cls, raw: Category) -> ParsedCategory:
        return cls(
            id = raw.get("id"),
            name = raw.get("name"),
            slug = raw.get("slug"),
            sport = ParsedSport.from_raw(raw.get("sport")),
            alpha2 = raw.get("alpha2"),
            flag = raw.get("flag"),
            country = ParsedCountry.from_raw(raw.get("country")),
        )
