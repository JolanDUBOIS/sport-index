from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from .base import BaseParsedModel
from .parsers import parse_timestamp
if TYPE_CHECKING:
    from .core import ParsedCategory
    from .team import ParsedTeam
    from sportindex.core.provider.raw.models import Season, UniqueTournament


@dataclass
class ParsedSeason(BaseParsedModel):
    id: int
    name: str
    year: str              # e.g. "24/25" or "2025"
    description: str
    startDateTimestamp: datetime

    @classmethod
    def _parse(cls, raw: Season) -> ParsedSeason:
        return cls(
            id=raw.get("id"),
            name=raw.get("name"),
            year=raw.get("year"),
            description=raw.get("description"),
            startDateTimestamp=parse_timestamp(raw.get("startDateTimestamp"))
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
    startDateTimestamp: datetime
    endDateTimestamp: datetime
    upperDivisions: list[ParsedUniqueTournament]
    lowerDivisions: list[ParsedUniqueTournament]
    titleHolder: ParsedTeam
    mostTitlesTeams: list[ParsedTeam]
    linkedUniqueTournaments: list[ParsedUniqueTournament]

    @classmethod
    def _parse(cls, raw: UniqueTournament) -> ParsedUniqueTournament:
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
            startDateTimestamp=parse_timestamp(raw.get("startDateTimestamp")),
            endDateTimestamp=parse_timestamp(raw.get("endDateTimestamp")),
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
    season: ParsedSeason
    uniqueTournament: ParsedUniqueTournament

    @classmethod
    def _parse(cls, raw: UniqueTournament) -> ParsedTournament:
        return cls(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            season=ParsedSeason.from_raw(raw.get("season")),
            uniqueTournament=ParsedUniqueTournament.from_raw(raw.get("uniqueTournament")),
        )
