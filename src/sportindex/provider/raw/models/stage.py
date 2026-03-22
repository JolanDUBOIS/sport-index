from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from .core import Category, Country
    from .primitives import Timestamp, Status
    from .team import Team


# =====================================================================
# Unique Stage
# =====================================================================

class UniqueStage(TypedDict, total=False):
    id: int
    slug: str
    name: str
    category: Category
    description: str


# =====================================================================
# Stage
# =====================================================================

class Stage(TypedDict, total=False):
    id: int
    slug: str
    name: str
    description: str
    year: str
    seasonStageName: str
    uniqueStage: UniqueStage
    type: StageType
    status: Status
    flag: str
    country: Country
    info: StageInfo
    startDateTimestamp: Timestamp
    endDateTimestamp: Timestamp
    stageParent: StageParent
    winner: Team
    substages: list[Stage]


# =====================================================================
# Primitives
# =====================================================================

class StageType(TypedDict, total=False):
    id: int
    name: str  # "Season", "Event", or other values — drives stage dispatch


class StageInfo(TypedDict, total=False):
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


class StageParent(TypedDict, total=False):
    id: int
    slug: str
    description: str
    startDateTimestamp: Timestamp
