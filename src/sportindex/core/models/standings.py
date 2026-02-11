from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional

from .core import BaseModel
from .team import Team
from .tournament import Tournament
from .utils import timestamp_to_iso


# === Standings entries ===

@dataclass(frozen=True)
class BaseStandingsEntry(BaseModel):
    team: Team
    points: int
    position: int
    id: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def _from_api(cls, raw: dict) -> BaseStandingsEntry:
        return BaseStandingsEntry(
            team=Team.from_api(raw.get("team")),
            points=raw.get("points"),
            position=raw.get("position"),
            id=raw.get("id"),
            updated_at=timestamp_to_iso(raw.get("updatedAtTimestamp"))
        )

@dataclass(frozen=True)
class RacingStandingsEntry(BaseStandingsEntry):
    victories: Optional[int] = None
    races_started: Optional[int] = None
    races_with_points: Optional[int] = None
    pole_positions: Optional[int] = None
    podiums: Optional[int] = None
    fastest_laps: Optional[int] = None

    @classmethod
    def _from_api(cls, raw: dict) -> RacingStandingsEntry:
        base_entry = BaseStandingsEntry._from_api(raw)
        return RacingStandingsEntry(
            **base_entry.to_dict(),
            victories=raw.get("victories"),
            races_started=raw.get("racesStarted"),
            races_with_points=raw.get("racesWithPoints"),
            pole_positions=raw.get("polePositions"),
            podiums=raw.get("podiums"),
            fastest_laps=raw.get("fastestLaps")
        )

@dataclass(frozen=True)
class TeamStandingsEntry(BaseStandingsEntry):
    matches: Optional[int] = None
    wins: Optional[int] = None
    draws: Optional[int] = None
    losses: Optional[int] = None
    scores_for: Optional[int] = None
    scores_against: Optional[int] = None
    score_difference: Optional[str] = None

    @classmethod
    def _from_api(cls, raw: dict) -> TeamStandingsEntry:
        base_entry = BaseStandingsEntry._from_api(raw)
        return TeamStandingsEntry(
            **base_entry.to_dict(),
            matches=raw.get("matches"),
            wins=raw.get("wins"),
            draws=raw.get("draws"),
            losses=raw.get("losses"),
            scores_for=raw.get("scoresFor"),
            scores_against=raw.get("scoresAgainst"),
            score_difference=raw.get("scoreDiffFormatted"),
        )


# === Standings ===

@dataclass(frozen=True)
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
            entries=[TeamStandingsEntry._from_api(entry) for entry in raw.get("rows", [])],
            tournament=Tournament.from_api(raw.get("tournament")),
            updated_at=timestamp_to_iso(raw.get("updatedAtTimestamp")),
            view=raw.get("type"),
        )

@dataclass(frozen=True)
class RacingStandings(BaseModel):
    entries: list[RacingStandingsEntry]

    @classmethod
    def _from_api(cls, raw: dict) -> RacingStandings:
        return RacingStandings(
            entries=[RacingStandingsEntry._from_api(entry) for entry in raw.get("standings", [])]
        )
