from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from .core import RawCategory, RawCountry
    from .primitives import Timestamp, RawStatus
    from .team import RawTeam


# =====================================================================
# Unique Stage
# =====================================================================

class RawUniqueStage(TypedDict, total=False):
    id: int
    slug: str
    name: str
    category: RawCategory
    description: str


# =====================================================================
# Stage
# =====================================================================

class RawStage(TypedDict, total=False):
    id: int
    slug: str
    name: str
    description: str
    year: str
    seasonStageName: str
    uniqueStage: RawUniqueStage
    type: RawStageType
    status: RawStatus
    flag: str
    country: RawCountry
    info: RawStageInfo
    startDateTimestamp: Timestamp
    endDateTimestamp: Timestamp
    stageParent: RawStageParent
    winner: RawTeam
    substages: list[RawStage]


# =====================================================================
# Primitives
# =====================================================================

class RawStageType(TypedDict, total=False):
    id: int
    name: str  # "Season", "Event", or other values — drives stage dispatch


class RawStageInfo(TypedDict, total=False):
    stageType: str     # e.g. "flat", "mountain", etc.
    stageRound: int
    discipline: str
    circuit: str       # Circuit name
    circuitCity: str
    circuitCountry: str
    circuitLength: float  # In meters
    trackCondition: str
    weather: str
    airTemperature: float
    trackTemperature: float
    humidity: float
    raceType: str      # e.g. "normal", "timetrial"
    laps: int
    raceDistance: int   # In meters
    lapsCompleted: int
    lapRecord: str
    departureCity: str  # Cycling stages
    arrivalCity: str


class RawStageParent(TypedDict, total=False):
    id: int
    slug: str
    description: str
    startDateTimestamp: Timestamp
