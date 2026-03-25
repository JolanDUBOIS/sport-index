from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from ..primitives import Timestamp
    from ..stage import RawStage
    from ..team import RawTeam


class RawRaceResults(TypedDict, total=False):
    position: int
    gridPosition: int
    points: int
    time: str               # Finishing time
    gap: str                # Gap to leader
    updatedAtTimestamp: int
    stage: RawStage


class RawSeasonCareerHistory(TypedDict, total=False):
    position: int
    points: int
    victories: int
    racesStarted: int
    polePositions: int
    podiums: int
    stage: RawStage
    parentTeam: RawTeam
    updatedAtTimestamp: Timestamp


class RawTotalCareerHistory(TypedDict, total=False):
    racesStarted: int
    victories: int
    podiums: int
    polePositions: int
    worldChampionshipTitles: int
    team: RawTeam


class RawDriverCareerHistory(TypedDict, total=False):
    total: RawTotalCareerHistory
    bySeason: list[RawSeasonCareerHistory]


class RawLap(TypedDict, total=False):
    lap: int
    position: int
    tyreType: str
    visitedPitStop: bool


class RawDriverPerformance(TypedDict, total=False):
    id: int
    name: str
    slug: str
    startNumber: int
    laps: list[RawLap]
    parentTeam: RawTeam
