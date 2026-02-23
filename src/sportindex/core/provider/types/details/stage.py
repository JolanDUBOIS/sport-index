from typing import TypedDict

from ..stages import RawStage
from ..entities import RawTeam


class RawRaceResults(TypedDict, total=False):
    stage: RawStage
    position: int
    gridPosition: int
    points: int
    time: str               # Finishing time
    gap: str                # Gap to leader
    updatedAtTimestamp: int


class RawSeasonCareerHistory(TypedDict, total=False):
    stage: RawStage
    position: int
    points: int
    victories: int
    racesStarted: int
    polePositions: int
    podiums: int
    parentTeam: RawTeam
    updatedAtTimestamp: int


class RawTotalCareerHistory(TypedDict, total=False):
    team: RawTeam
    racesStarted: int
    victories: int
    podiums: int
    polePositions: int
    worldChampionshipTitles: int


class RawDriverCareerHistory(TypedDict, total=False):
    total: RawTotalCareerHistory
    bySeason: list[RawSeasonCareerHistory]


class RawLap(TypedDict, total=False):
    """A single lap from a driver's race performance."""
    lap: int
    position: int
    tyreType: str
    visitedPitStop: bool


class RawDriverPerformance(TypedDict, total=False):
    """Driver performance in a stage, including per-lap data.

    Returned by the ``drivers-performance`` endpoint.
    """
    id: int
    name: str
    slug: str
    parentTeam: RawTeam
    startNumber: int
    laps: list[RawLap]
