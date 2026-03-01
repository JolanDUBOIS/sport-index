from __future__ import annotations

from datetime import datetime

from .base import BaseModel, RawModel, ParsedModel
from .common import Category, Country
from .primitives import Timestamp, Status
from .team import RawTeam


# =====================================================================
# Unique Stage
# =====================================================================

class UniqueStage(BaseModel):
    id: int
    slug: str
    name: str
    category: Category
    description: str


# =====================================================================
# Primitives
# =====================================================================

class StageType(BaseModel):
    id: int
    name: str  # "Season", "Event", or other values — drives stage dispatch


class StageInfo(BaseModel):
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


class StageParent(BaseModel):
    id: int
    slug: str
    description: str

class RawStageParent(StageParent, RawModel):
    startDateTimestamp: Timestamp

class ParsedStageParent(StageParent, ParsedModel):
    startDateTimestamp: datetime


class Stage(BaseModel):
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

class RawStage(Stage, RawModel):
    startDateTimestamp: Timestamp
    endDateTimestamp: Timestamp
    stageParent: RawStageParent
    winner: RawTeam
    substages: list[RawStage]

class ParsedStage(Stage, ParsedModel):
    startDateTimestamp: datetime
    endDateTimestamp: datetime
    stageParent: ParsedStageParent
    winner: RawTeam
    substages: list[ParsedStage]
