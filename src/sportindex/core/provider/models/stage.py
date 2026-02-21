from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .common import Status
from .core import BaseModel, Country, Category
from .participants import Team
from .utils import timestamp_to_iso


# --- Details models for stages ---

@dataclass(frozen=True, kw_only=True)
class Circuit(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    country_name: Optional[str] = None
    length: Optional[float] = None # in meters

    @classmethod
    def _from_api(cls, raw: dict) -> Circuit:
        return Circuit(
            name=raw.get("circuit"),
            city=raw.get("circuitCity"),
            country_name=raw.get("circuitCountry"),
            length=raw.get("circuitLength"),
        )

@dataclass(frozen=True, kw_only=True)
class WeatherConditions(BaseModel):
    track_conditions: Optional[str] = None
    weather: Optional[str] = None
    air_temperature: Optional[float] = None
    track_temperature: Optional[float] = None
    humidity: Optional[float] = None

    @classmethod
    def _from_api(cls, raw: dict) -> WeatherConditions:
        return WeatherConditions(
            track_conditions=raw.get("trackCondition"),
            weather=raw.get("weather"),
            air_temperature=raw.get("airTemperature"),
            track_temperature=raw.get("trackTemperature"),
            humidity=raw.get("humidity"),
        )

@dataclass(frozen=True, kw_only=True)
class RaceStats(BaseModel):
    kind: Optional[str] = None # e.g. "Circuit", "Point-to-point", etc.
    laps: Optional[int] = None
    distance: Optional[int] = None # in meters
    laps_completed: Optional[int] = None
    lap_record: Optional[str] = None
    departure_city: Optional[str] = None # e.g. for cycling stages
    arrival_city: Optional[str] = None

    @classmethod
    def _from_api(cls, raw: dict) -> RaceStats:
        return RaceStats(
            kind=raw.get("raceType"),
            laps=raw.get("laps"),
            distance=raw.get("raceDistance"),
            laps_completed=raw.get("lapsCompleted"),
            lap_record=raw.get("lapRecord"),
            departure_city=raw.get("departureCity"),
            arrival_city=raw.get("arrivalCity"),
        )

@dataclass(frozen=True, kw_only=True)
class StageDetails(BaseModel):
    kind: Optional[str] = None # e.g. "Mountain", "Sprint", etc.
    round: Optional[int] = None
    discipline: Optional[str] = None
    circuit: Optional[Circuit] = None
    weather: Optional[WeatherConditions] = None
    race_stats: Optional[RaceStats] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Optional[StageDetails]:
        return StageDetails(
            kind=raw.get("stageType"),
            round=raw.get("stageRound"),
            discipline=raw.get("discipline"),
            circuit=Circuit.from_api(raw),
            weather=WeatherConditions.from_api(raw),
            race_stats=RaceStats.from_api(raw),
        )


# --- Main stage models ---

@dataclass(frozen=True, kw_only=True)
class BaseStage(BaseModel):
    id: str
    slug: str
    name: str
    description: Optional[str] = None

    @classmethod
    def _from_api(cls, raw: dict) -> BaseStage:
        return BaseStage(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            description=raw.get("description"),
        )

@dataclass(frozen=True, kw_only=True)
class UniqueStage(BaseStage):
    category: Category
    country: Country

    @classmethod
    def _from_api(cls, raw: dict) -> UniqueStage:
        return UniqueStage(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            description=raw.get("description"),
            category=Category.from_api(raw.get("category")),
            country=Country.from_api(raw.get("country")),
        )

@dataclass(frozen=True, kw_only=True)
class Stage(BaseStage):
    year: str
    start: str
    kind: str # e.g. "Season", "Event", "Stage", etc.
    status: Status
    end: Optional[str] = None
    flag: Optional[str] = None
    winner: Optional[Team] = None
    country: Optional[Country] = None
    unique_stage: Optional[UniqueStage] = None
    parent_stage: Optional[BaseStage] = None
    season_stage_name: Optional[str] = None
    details: Optional[StageDetails] = None
    substages: Optional[list[Stage]] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Stage:
        return Stage(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            description=raw.get("description"),
            year=raw.get("year"),
            start=timestamp_to_iso(raw.get("startDateTimestamp")),
            kind=raw.get("type", {}).get("name"),
            status=Status.from_api(raw.get("status")),
            end=timestamp_to_iso(raw.get("endDateTimestamp")),
            flag=raw.get("flag"),
            winner=Team.from_api(raw.get("winner")),
            country=Country.from_api(raw.get("country")),
            unique_stage=UniqueStage.from_api(raw.get("uniqueStage")),
            parent_stage=BaseStage.from_api(raw.get("stageParent")),
            season_stage_name=raw.get("seasonStageName"),
            details=StageDetails.from_api(raw.get("info")),
            substages=[Stage.from_api(sub) for sub in raw.get("substages", [])],
        )
