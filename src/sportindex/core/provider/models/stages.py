"""
Stage and race dataclass types: motorsport, cycling, multi-event sports.

See __init__.py for full package docstring and conventions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import RawModel

if TYPE_CHECKING:
    from .common import RawCategory, RawCountry
    from .entities import RawTeam
    from .primitives import RawStatus, Timestamp


# =====================================================================
# Stage (Motorsport / Cycling / Multi-event sports)
# =====================================================================

class RawUniqueStage(RawModel):
    id: int
    slug: str
    name: str
    category: RawCategory
    description: str


class RawStageParent(RawModel):
    id: int
    slug: str
    description: str
    startDateTimestamp: int


class RawStageType(RawModel):
    id: int
    name: str  # "Season", "Event", or other values — drives stage dispatch


class RawStageInfo(RawModel):
    """The ``info`` dict on a stage, containing circuit/weather/race details.
    All keys are at the top level of the ``info`` dict (not further nested).
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


class RawStage(RawModel):
    """A stage can be a Season, Event, or SubStage — check ``type.name`` to
    dispatch. Substages may be nested recursively.

    REMARK: The current code uses class inheritance for SeasonStage/EventStage/
    SubStage dispatch. With dataclasses you typically check `type.name` directly.
    """
    id: int
    slug: str
    name: str
    description: str
    year: str
    startDateTimestamp: Timestamp
    endDateTimestamp: Timestamp
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
