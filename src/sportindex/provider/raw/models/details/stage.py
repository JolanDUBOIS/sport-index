from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from ..primitives import Timestamp
    from ..stage import Stage
    from ..team import Team


class RaceResults(TypedDict, total=False):
    position: int
    gridPosition: int
    points: int
    time: str               # Finishing time
    gap: str                # Gap to leader
    updatedAtTimestamp: int
    stage: Stage


class SeasonCareerHistory(TypedDict, total=False):
    position: int
    points: int
    victories: int
    racesStarted: int
    polePositions: int
    podiums: int
    stage: Stage
    parentTeam: Team
    updatedAtTimestamp: Timestamp


class TotalCareerHistory(TypedDict, total=False):
    racesStarted: int
    victories: int
    podiums: int
    polePositions: int
    worldChampionshipTitles: int
    team: Team


class DriverCareerHistory(TypedDict, total=False):
    total: TotalCareerHistory
    bySeason: list[SeasonCareerHistory]


class Lap(TypedDict, total=False):
    lap: int
    position: int
    tyreType: str
    visitedPitStop: bool


class DriverPerformance(TypedDict, total=False):
    id: int
    name: str
    slug: str
    startNumber: int
    laps: list[Lap]
    parentTeam: Team
