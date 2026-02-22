"""
Stage and race TypedDict types: motorsport, cycling, multi-event sports.

See __init__.py for full package docstring and conventions.
"""

from __future__ import annotations

from typing import TypedDict

from .common import RawCategory, RawCountry, RawStatus
from .entities import RawTeam


# =====================================================================
# Stage (Motorsport / Cycling / Multi-event sports)
# =====================================================================

class RawUniqueStage(TypedDict, total=False):
    id: int
    slug: str
    name: str
    category: RawCategory
    description: str


class RawStageParent(TypedDict, total=False):
    id: int
    slug: str
    description: str
    startDateTimestamp: int


class RawStageType(TypedDict, total=False):
    id: int
    name: str  # "Season", "Event", or other values — drives stage dispatch


class RawStageInfo(TypedDict, total=False):
    """The ``info`` dict on a stage, containing circuit/weather/race details.
    All keys are at the top level of the ``info`` dict (not further nested).

    REMARK: Fields like circuit/weather appear in the same flat dict.
    The current code dispatches them into separate Circuit, WeatherConditions,
    RaceStats classes — consider whether that grouping is useful in your
    higher layer.
    """
    # Stage metadata
    stageType: str     # e.g. "Mountain", "Sprint"
    stageRound: int
    discipline: str
    # Circuit info
    circuit: str       # Circuit name
    circuitCity: str
    circuitCountry: str
    circuitLength: float  # In meters — ASSUMPTION
    # Weather
    trackCondition: str
    weather: str
    airTemperature: float
    trackTemperature: float
    humidity: float
    # Race stats
    raceType: str      # e.g. "Circuit", "Point-to-point"
    laps: int
    raceDistance: int   # In meters — ASSUMPTION
    lapsCompleted: int
    lapRecord: str
    departureCity: str  # Cycling stages
    arrivalCity: str


class RawStage(TypedDict, total=False):
    """A stage can be a Season, Event, or SubStage — check ``type.name`` to
    dispatch. Substages may be nested recursively.

    REMARK: The current code uses class inheritance for SeasonStage/EventStage/
    SubStage dispatch. With TypedDicts you just check type["name"] directly.
    """
    id: int
    slug: str
    name: str
    description: str
    year: str
    startDateTimestamp: int
    endDateTimestamp: int
    seasonStageName: str
    uniqueStage: RawUniqueStage
    stageParent: RawStageParent
    type: RawStageType
    # Exist on EventStage / SubStage only:
    status: RawStatus
    flag: str
    winner: RawTeam
    country: RawCountry
    info: RawStageInfo
    # Nested substages (SeasonStage → EventStages, EventStage → SubStages)
    substages: list[RawStage]         # ASSUMPTION: API nests them under 'substages'


class RawRace(TypedDict, total=False):
    """A race entry — combines stage data with finishing metadata.

    Returned by endpoints that list a team/driver's races within a season
    stage (e.g. ``/team/{id}/stage-season/{id}/races``).
    """
    stage: RawStage
    position: int
    gridPosition: int
    points: int
    time: str               # Finishing time
    gap: str                # Gap to leader
    updatedAtTimestamp: int


# =====================================================================
# Driver performance (per-lap data)
# =====================================================================

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
