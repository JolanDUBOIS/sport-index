"""
Stage and race TypedDict types: motorsport, cycling, multi-event sports.

See __init__.py for full package docstring and conventions.
"""

from __future__ import annotations

from typing import TypedDict

from .common import RawCategory, RawCountry
from .entities import RawTeam
from .primitives import RawStatus


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
    stageType: str     # e.g. "flat", "mountain", etc.
    stageRound: int
    discipline: str
    # Circuit info
    circuit: str       # Circuit name
    circuitCity: str
    circuitCountry: str
    circuitLength: float  # In meters
    # Weather
    trackCondition: str
    weather: str
    airTemperature: float
    trackTemperature: float
    humidity: float
    # Race stats
    raceType: str      # e.g. "normal", "timetrial"
    laps: int
    raceDistance: int   # In meters
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
    status: RawStatus
    flag: str
    winner: RawTeam
    country: RawCountry
    info: RawStageInfo
    substages: list[RawStage]
