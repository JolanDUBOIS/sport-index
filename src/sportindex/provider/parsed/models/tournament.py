from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from .base import BaseParsedModel
from .parsers import parse_timestamp
if TYPE_CHECKING:
    from .core import ParsedCategory
    from .team import ParsedTeam
    from sportindex.provider.raw import RawSeason, RawUniqueTournament, RawTournament


@dataclass
class ParsedSeason(BaseParsedModel):
    id: int
    name: str
    year: str              # e.g. "24/25" or "2025"
    description: str
    start: datetime

    @classmethod
    def _parse(cls, raw: RawSeason) -> ParsedSeason:
        return cls(
            id=raw.get("id"),
            name=raw.get("name"),
            year=raw.get("year"),
            description=raw.get("description"),
            start=parse_timestamp(raw.get("startDateTimestamp"))
        )


@dataclass
class ParsedUniqueTournament(BaseParsedModel):
    id: int
    slug: str
    name: str
    category: ParsedCategory
    gender: str
    tier: str
    titleHolderTitles: int
    mostTitles: int
    hasRounds: bool
    hasGroups: bool
    hasPlayoffSeries: bool
    groundType: str         # e.g. "Red clay", "Grass", etc.
    numberOfSets: int
    tennisPoints: int
    start: datetime
    end: datetime
    upperDivisions: list[ParsedUniqueTournament]
    lowerDivisions: list[ParsedUniqueTournament]
    titleHolder: ParsedTeam
    mostTitlesTeams: list[ParsedTeam]
    linkedUniqueTournaments: list[ParsedUniqueTournament]

    @classmethod
    def _parse(cls, raw: RawUniqueTournament) -> ParsedUniqueTournament:
        from .core import ParsedCategory
        from .team import ParsedTeam
        return cls(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            category=ParsedCategory.from_raw(raw.get("category")),
            gender=raw.get("gender"),
            tier=raw.get("tier"),
            titleHolderTitles=raw.get("titleHolderTitles"),
            mostTitles=raw.get("mostTitles"),
            hasRounds=raw.get("hasRounds"),
            hasGroups=raw.get("hasGroups"),
            hasPlayoffSeries=raw.get("hasPlayoffSeries"),
            groundType=raw.get("groundType"),
            numberOfSets=raw.get("numberOfSets"),
            tennisPoints=raw.get("tennisPoints"),
            start=parse_timestamp(raw.get("startDateTimestamp")),
            end=parse_timestamp(raw.get("endDateTimestamp")),
            upperDivisions=[cls.from_raw(t) for t in raw.get("upperDivisions", [])],
            lowerDivisions=[cls.from_raw(t) for t in raw.get("lowerDivisions", [])],
            titleHolder=ParsedTeam.from_raw(raw.get("titleHolder")) if raw.get("titleHolder") else None,
            mostTitlesTeams=[ParsedTeam.from_raw(t) for t in raw.get("mostTitlesTeams", [])],
            linkedUniqueTournaments=[cls.from_raw(t) for t in raw.get("linkedUniqueTournaments", [])],
        )


@dataclass
class ParsedTournament(BaseParsedModel):
    id: int
    slug: str
    name: str
    category: ParsedCategory
    uniqueTournament: ParsedUniqueTournament

    @classmethod
    def _parse(cls, raw: RawTournament) -> ParsedTournament:
        from .core import ParsedCategory
        return cls(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            category=ParsedCategory.from_raw(raw.get("category")),
            uniqueTournament=ParsedUniqueTournament.from_raw(raw.get("uniqueTournament")),
        )
