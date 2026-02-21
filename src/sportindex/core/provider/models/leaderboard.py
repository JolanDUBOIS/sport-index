from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal

from .core import BaseModel, Country, Sport, Category
from .event import Event
from .participants import Team
from .tournament import UniqueTournament, Tournament
from .utils import timestamp_to_iso, get_nested


# === Team/Individual Sports Standings ===

@dataclass(frozen=True, kw_only=True)
class Promotion(BaseModel):
    id: str
    name: str

    @classmethod
    def _from_api(cls, raw: dict) -> Promotion:
        return Promotion(
            id=raw.get("id"),
            name=raw.get("text"),
        )

@dataclass(frozen=True, kw_only=True)
class TeamStandingsEntry(BaseModel):
    id: str
    team: Team
    position: int
    matches: int
    wins: int
    draws: int
    losses: int
    points: Optional[int] = None
    percentage: Optional[float] = None
    scores_for: Optional[int] = None
    scores_against: Optional[int] = None
    score_difference: Optional[str] = None
    promotion: Optional[Promotion] = None
    games_behind: Optional[int] = None
    streak: Optional[int] = None

    @classmethod
    def _from_api(cls, raw: dict) -> TeamStandingsEntry:
        return TeamStandingsEntry(
            id=raw.get("id"),
            team=Team.from_api(raw.get("team")),
            position=raw.get("position"),
            matches=raw.get("matches"),
            wins=raw.get("wins"),
            draws=raw.get("draws"),
            losses=raw.get("losses"),
            points=raw.get("points"),
            percentage=raw.get("percentage"),
            scores_for=raw.get("scoresFor"),
            scores_against=raw.get("scoresAgainst"),
            score_difference=raw.get("scoreDiffFormatted"),
            promotion=Promotion.from_api(raw.get("promotion")),
            games_behind=raw.get("gamesBehind"),
            streak=raw.get("streak"),
        )

@dataclass(frozen=True, kw_only=True)
class TeamStandings(BaseModel):
    id: str
    name: str
    entries: list[TeamStandingsEntry]
    tournament: Tournament
    updated_at: Optional[str] = None
    view: Optional[Literal["home", "away", "total"]] = None

    @classmethod
    def _from_api(cls, raw: dict) -> TeamStandings:
        return TeamStandings(
            id=raw.get("id"),
            name=raw.get("name"),
            entries=[TeamStandingsEntry.from_api(entry) for entry in raw.get("rows", [])],
            tournament=Tournament.from_api(raw.get("tournament")),
            updated_at=timestamp_to_iso(raw.get("updatedAtTimestamp")),
            view=raw.get("type"),
        )


# === Racing Sports Standings ===

@dataclass(frozen=True, kw_only=True)
class RacingStandingsEntry(BaseModel):
    team: Team
    position: int
    time: Optional[str] = None
    interval: Optional[str] = None
    gap: Optional[str] = None
    points: Optional[int] = None
    updated_at: Optional[str] = None
    victories: Optional[int] = None
    races_started: Optional[int] = None
    races_with_points: Optional[int] = None
    pole_positions: Optional[int] = None
    podiums: Optional[int] = None
    fastest_laps: Optional[int] = None
    parent_team: Optional[Team] = None

    @classmethod
    def _from_api(cls, raw: dict) -> RacingStandingsEntry:
        return RacingStandingsEntry(
            team=Team.from_api(raw.get("team")),
            position=raw.get("position"),
            time=raw.get("time"),
            interval=raw.get("interval"),
            gap=raw.get("gap"),
            points=raw.get("points"),
            updated_at=timestamp_to_iso(raw.get("updatedAtTimestamp")),
            victories=raw.get("victories"),
            races_started=raw.get("racesStarted"),
            races_with_points=raw.get("racesWithPoints"),
            pole_positions=raw.get("polePositions"),
            podiums=raw.get("podiums"),
            fastest_laps=raw.get("fastestLaps"),
            parent_team=Team.from_api(raw.get("parentTeam")),
        )

@dataclass(frozen=True, kw_only=True)
class RacingStandings(BaseModel):
    view: Literal["competitors", "teams"]
    entries: list[RacingStandingsEntry]

    @classmethod
    def _from_api(cls, raw: dict) -> RacingStandings:
        return RacingStandings(
            view=raw.get("view", ""),
            entries=[RacingStandingsEntry.from_api(entry) for entry in raw.get("standings", [])]
        )


# === Rankings ===

@dataclass(frozen=True, kw_only=True)
class RankingEntry(BaseModel):
    id: str
    position: int
    team: Team
    points: float
    country: Optional[Country] = None
    previous_position: Optional[int] = None
    previous_points: Optional[float] = None
    last_event: Optional[Event] = None
    updated_at: Optional[str] = None

    @classmethod
    def _from_api(cls, raw: dict) -> RankingEntry:
        return RankingEntry(
            id=raw.get("id"),
            position=raw.get("position"),
            team=Team.from_api(raw.get("team")),
            points=raw.get("points"),
            country=Country.from_api(raw.get("country")),
            previous_position=raw.get("previousPosition"),
            previous_points=raw.get("previousPoints"),
            last_event=Event.from_api(raw.get("lastEvent")),
            updated_at=timestamp_to_iso(raw.get("updatedTimestamp")),
        )

@dataclass(frozen=True, kw_only=True)
class Rankings(BaseModel):
    id: str
    slug: str
    name: str
    gender: str
    sport: Sport
    category: Category
    rankings: list[RankingEntry]
    unique_tournament: Optional[UniqueTournament] = None
    updated_at: Optional[str] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Rankings:
        return Rankings(
            id=get_nested(raw, "rankingType.id"),
            slug=get_nested(raw, "rankingType.slug"),
            name=get_nested(raw, "rankingType.name"),
            gender=get_nested(raw, "rankingType.gender"),
            sport=Sport.from_api(get_nested(raw, "rankingType.sport")),
            category=Category.from_api(get_nested(raw, "rankingType.category")),
            unique_tournament=UniqueTournament.from_api(get_nested(raw, "rankingType.uniqueTournament")),
            rankings=[RankingEntry.from_api(entry) for entry in raw.get("rankingRows", [])],
            updated_at=timestamp_to_iso(get_nested(raw, "rankingType.lastUpdatedTimestamp")),
        )
