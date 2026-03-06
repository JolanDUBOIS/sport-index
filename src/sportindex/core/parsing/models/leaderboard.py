from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from .base import BaseParsedModel
from .parsers import parse_timestamp
if TYPE_CHECKING:
    from .event import ParsedEvent
    from .team import ParsedTeam
    from .tournament import ParsedTournament, ParsedUniqueTournament
    from sportindex.core.provider.models import (
        TeamStandingsEntry, TeamStandings,
        RacingStandingsEntry, RankingEntry,
        RankingType, Promotion, Sport,
        Category, Country
    )


@dataclass
class ParsedTeamStandingsEntry(BaseParsedModel):
    id: int
    position: int
    matches: int
    wins: int
    draws: int
    losses: int
    points: int
    percentage: float          # Win percentage
    scoresFor: int
    scoresAgainst: int
    scoreDiffFormatted: str    # e.g. "+15"
    promotion: Promotion
    gamesBehind: int
    streak: int
    team: ParsedTeam

    @classmethod
    def _parse(cls, raw: TeamStandingsEntry) -> ParsedTeamStandingsEntry:
        from .team import ParsedTeam
        return cls(
            id=raw.get("id"),
            position=raw.get("position"),
            matches=raw.get("matches"),
            wins=raw.get("wins"),
            draws=raw.get("draws"),
            losses=raw.get("losses"),
            points=raw.get("points"),
            percentage=raw.get("percentage"),
            scoresFor=raw.get("scoresFor"),
            scoresAgainst=raw.get("scoresAgainst"),
            scoreDiffFormatted=raw.get("scoreDiffFormatted"),
            promotion=raw.get("promotion"),
            gamesBehind=raw.get("gamesBehind"),
            streak=raw.get("streak"),
            team=ParsedTeam.from_raw(raw.get("team"))
        )


@dataclass
class ParsedTeamStandings(BaseParsedModel):
    id: int
    name: str                  # e.g. "Premier League"
    type_: str                  # "home", "away", "total"
    rows: list[ParsedTeamStandingsEntry]
    tournament: ParsedTournament
    updatedAt: datetime

    @classmethod
    def _parse(cls, raw: TeamStandings) -> ParsedTeamStandings:
        from .tournament import ParsedTournament
        return cls(
            id=raw.get("id"),
            name=raw.get("name"),
            type_=raw.get("type"),
            rows=[ParsedTeamStandingsEntry.from_raw(entry) for entry in raw.get("rows", [])],
            tournament=ParsedTournament.from_raw(raw.get("tournament")),
            updatedAt=parse_timestamp(raw.get("updatedAtTimestamp"))
        )


@dataclass
class ParsedRacingStandingsEntry(BaseParsedModel):
    startNumber: int           # Driver or cyclist number
    number: int                # alternative numbering, if API provides
    team: ParsedTeam
    parentTeam: ParsedTeam
    updatedAt: datetime

    # Position / Result
    position: int
    points: int
    interval: str              # Interval to competitor ahead
    gap: str                   # Gap to leader
    totalTime: str
    time: str

    # Race-specific stats (Motorsport)
    gridPosition: int
    laps: int
    lapsLed: int
    victories: int
    racesStarted: int
    racesWithPoints: int
    polePositions: int
    podiums: int
    fastestLaps: int
    fastestLapTime: str
    personalFastestLap: int    # Which lap was driver's personal fastest
    personalFastestLapTime: str
    pitStops: int
    tyreType: str
    tyreState: str

    # Cycling-specific
    sprint: int
    climb: int
    sprintPosition: int
    climbPosition: int
    shirt: str

    @classmethod
    def _parse(cls, raw: RacingStandingsEntry) -> ParsedRacingStandingsEntry:
        from .team import ParsedTeam
        return cls(
            startNumber=raw.get("startNumber"),
            number=raw.get("number"),
            team=ParsedTeam.from_raw(raw.get("team")),
            parentTeam=ParsedTeam.from_raw(raw.get("parentTeam")) if raw.get("parentTeam") else None,
            updatedAt=parse_timestamp(raw.get("updatedAtTimestamp")),
            position=raw.get("position"),
            points=raw.get("points"),
            interval=raw.get("interval"),
            gap=raw.get("gap"),
            totalTime=raw.get("totalTime"),
            time=raw.get("time"),
            gridPosition=raw.get("gridPosition"),
            laps=raw.get("laps"),
            lapsLed=raw.get("lapsLed"),
            victories=raw.get("victories"),
            racesStarted=raw.get("racesStarted"),
            racesWithPoints=raw.get("racesWithPoints"),
            polePositions=raw.get("polePositions"),
            podiums=raw.get("podiums"),
            fastestLaps=raw.get("fastestLaps"),
            fastestLapTime=raw.get("fastestLapTime"),
            personalFastestLap=raw.get("personalFastestLap"),
            personalFastestLapTime=raw.get("personalFastestLapTime"),
            pitStops=raw.get("pitStops"),
            tyreType=raw.get("tyreType"),
            tyreState=raw.get("tyreState"),
            sprint=raw.get("sprint"),
            climb=raw.get("climb"),
            sprintPosition=raw.get("sprintPosition"),
            climbPosition=raw.get("climbPosition"),
            shirt=raw.get("shirt")
        )


@dataclass
class ParsedRankingType(BaseParsedModel):
    id: int
    slug: str
    name: str
    gender: str
    sport: Sport
    category: Category
    uniqueTournament: ParsedUniqueTournament
    lastUpdated: datetime

    @classmethod
    def _parse(cls, raw: RankingType) -> ParsedRankingType:
        from .tournament import ParsedUniqueTournament
        return cls(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            gender=raw.get("gender"),
            sport=raw.get("sport"),
            category=raw.get("category"),
            uniqueTournament=ParsedUniqueTournament.from_raw(raw.get("uniqueTournament")),
            lastUpdated=parse_timestamp(raw.get("lastUpdated"))
        )


@dataclass
class ParsedRankingEntry(BaseParsedModel):
    id: int
    name: str
    position: int         # For MMA, position starts at 0 instead of 1
    points: float
    country: Country
    bestPosition: int
    previousPosition: int
    previousPoints: float
    tournamentsPlayed: int
    team: ParsedTeam
    lastEvent: ParsedEvent
    updatedAt: datetime

    @classmethod
    def _parse(cls, raw: RankingEntry) -> ParsedRankingEntry:
        from .team import ParsedTeam
        from .event import ParsedEvent
        return cls(
            id=raw.get("id"),
            name=raw.get("name"),
            position=raw.get("position"),
            points=raw.get("points"),
            country=raw.get("country"),
            bestPosition=raw.get("bestPosition"),
            previousPosition=raw.get("previousPosition"),
            previousPoints=raw.get("previousPoints"),
            tournamentsPlayed=raw.get("tournamentsPlayed"),
            team=ParsedTeam.from_raw(raw.get("team")),
            lastEvent=ParsedEvent.from_raw(raw.get("lastEvent")) if raw.get("lastEvent") else None,
            updatedAt=parse_timestamp(raw.get("updatedAtTimestamp"))
        )
