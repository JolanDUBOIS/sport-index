from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional

from .core import BaseModel
from .team import Team
from .tournament import Tournament
from .utils import timestamp_to_iso


# === Team/Individual Sports Standings ===

@dataclass(frozen=True, kw_only=True)
class PromotionInfo(BaseModel):
    id: str
    name: str

    @classmethod
    def _from_api(cls, raw: dict) -> PromotionInfo:
        return PromotionInfo(
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
    promotion: Optional[PromotionInfo] = None
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
            promotion=PromotionInfo.from_api(raw.get("promotion")),
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
    kind: str
    entries: list[RacingStandingsEntry]

    @classmethod
    def _from_api(cls, raw: dict) -> RacingStandings:
        return RacingStandings(
            kind=raw.get("kind", ""),
            entries=[RacingStandingsEntry.from_api(entry) for entry in raw.get("standings", [])]
        )
