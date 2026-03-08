from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from .base import BaseParsedModel
from .parsers import parse_timestamp
if TYPE_CHECKING:
    from .main import ParsedSport, ParsedCountry, ParsedCategory
    from .manager import ParsedManager
    from .tournament import ParsedTournament, ParsedUniqueTournament
    from .venue import ParsedVenue
    from sportindex.core.provider.raw.models import (
        Team, Amount, PlayerTeamInfo
    )


@dataclass
class ParsedTeam(BaseParsedModel):
    id: int
    slug: str
    name: str
    shortName: str
    fullName: str
    nameCode: str        # e.g. "PSG", "BAR"
    gender: str          # "M", "F"
    sport: ParsedSport
    category: ParsedCategory
    country: ParsedCountry
    national: bool
    disabled: bool
    ranking: int
    tournament: ParsedTournament
    primaryUniqueTournament: ParsedUniqueTournament
    manager: ParsedManager
    venue: ParsedVenue
    foundationDateTimestamp: datetime
    parentTeam: ParsedTeam
    playerTeamInfo: ParsedPlayerTeamInfo

    @classmethod
    def _parse(cls, raw: Team) -> ParsedTeam:
        from .main import ParsedSport, ParsedCountry, ParsedCategory
        from .manager import ParsedManager
        from .tournament import ParsedTournament, ParsedUniqueTournament
        from .venue import ParsedVenue
        return cls(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            shortName=raw.get("shortName"),
            fullName=raw.get("fullName"),
            nameCode=raw.get("nameCode"),
            gender=raw.get("gender"),
            sport=ParsedSport.from_raw(raw.get("sport")),
            category=ParsedCategory.from_raw(raw.get("category")),
            country=ParsedCountry.from_raw(raw.get("country")),
            national=raw.get("national"),
            disabled=raw.get("disabled"),
            ranking=raw.get("ranking"),
            tournament=ParsedTournament.from_raw(raw.get("tournament")),
            primaryUniqueTournament=ParsedUniqueTournament.from_raw(raw.get("primaryUniqueTournament")),
            manager=ParsedManager.from_raw(raw.get("manager")),
            venue=ParsedVenue.from_raw(raw.get("venue")),
            foundationDateTimestamp=parse_timestamp(raw.get("foundationDateTimestamp")),
            parentTeam=cls.from_raw(raw.get("parentTeam")) if raw.get("parentTeam") else None,
            playerTeamInfo=ParsedPlayerTeamInfo.from_raw(raw.get("playerTeamInfo")) if raw.get("playerTeamInfo") else None,
        )

@dataclass
class ParsedPlayerTeamInfo(BaseParsedModel):
    id: int
    residence: str
    birthplace: str
    height: float        # in m (e.g. 1.85)
    weight: float        # in kg
    number: int
    plays: str           # e.g. "right-handed"
    mainDriver: bool
    turnedPro: str       # e.g. "2018"
    prizeCurrentRaw: Amount
    prizeTotalRaw: Amount
    currentRanking: int
    birthDateTimestamp: datetime

    @classmethod
    def _parse(cls, raw: PlayerTeamInfo) -> ParsedPlayerTeamInfo:
        return cls(
            id=raw.get("id"),
            residence=raw.get("residence"),
            birthplace=raw.get("birthplace"),
            height=raw.get("height"),
            weight=raw.get("weight"),
            number=raw.get("number"),
            plays=raw.get("plays"),
            mainDriver=raw.get("mainDriver"),
            turnedPro=raw.get("turnedPro"),
            prizeCurrentRaw=raw.get("prizeCurrentRaw"),
            prizeTotalRaw=raw.get("prizeTotalRaw"),
            currentRanking=raw.get("currentRanking"),
            birthDateTimestamp=parse_timestamp(raw.get("birthDateTimestamp")),
        )
