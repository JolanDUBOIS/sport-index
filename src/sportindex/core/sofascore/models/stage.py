from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .category import Category
from .core import BaseModel, Country, Status
from .utils import timestamp_to_iso


@dataclass(frozen=True)
class Circuit(BaseModel):
    city: Optional[str] = None
    country_name: Optional[str] = None
    name: Optional[str] = None
    version: Optional[str] = None
    length: Optional[float] = None # in meters

    @classmethod
    def _from_api(cls, raw: dict) -> Circuit:
        return Circuit(
            city=raw.get("circuitCity"),
            country_name=raw.get("circuitCountry"),
            name=raw.get("circuit"),
            version=raw.get("version"),
            length=raw.get("circuitLength"),
        )

@dataclass(frozen=True)
class RaceInfo(BaseModel):
    laps: Optional[int] = None
    distance: Optional[float] = None # in meters

    @classmethod
    def _from_api(cls, raw: dict) -> RaceInfo:
        return RaceInfo(
            laps=raw.get("laps"),
            distance=raw.get("raceDistance"),
        )


@dataclass(frozen=True)
class UniqueStage(BaseModel):
    id: str
    slug: str
    name: str
    category: Category

    @classmethod
    def _from_api(cls, raw: dict) -> UniqueStage:
        return UniqueStage(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            category=Category.from_api(raw.get("category"))
        )

@dataclass(frozen=True)
class SeasonStage(BaseModel):
    id: str
    slug: str
    name: str
    year: str
    start: Optional[str] = None
    description: Optional[str] = None
    unique_stage: Optional[UniqueStage] = None
    substages: Optional[list[RoundStage]] = None

    @classmethod
    def _from_api(cls, raw: dict) -> SeasonStage:
        return SeasonStage(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            year=raw.get("year"),
            start=timestamp_to_iso(raw.get("startDateTimestamp")),
            description=raw.get("description"),
            unique_stage=UniqueStage.from_api(raw.get("uniqueStage")),
            substages=[RoundStage.from_api(sub) for sub in raw.get("substages", [])]
        )

@dataclass(frozen=True)
class RoundStage(BaseModel):
    id: str
    slug: str
    name: str
    year: str
    start: str
    end: str
    info: Optional[RaceInfo] = None
    status: Optional[Status] = None
    circuit: Optional[Circuit] = None
    country: Optional[Country] = None
    description: Optional[str] = None
    unique_stage: Optional[UniqueStage] = None
    substages: Optional[list[SessionStage]] = None

    @classmethod
    def _from_api(cls, raw: dict) -> RoundStage:
        return RoundStage(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            year=raw.get("year"),
            start=timestamp_to_iso(raw.get("startDateTimestamp")),
            end=timestamp_to_iso(raw.get("endDateTimestamp")),
            info=RaceInfo.from_api(raw.get("info")),
            status=Status.from_api(raw.get("status")),
            circuit=Circuit.from_api(raw.get("info")),
            country=Country.from_api(raw.get("country")),
            description=raw.get("description"),
            unique_stage=UniqueStage.from_api(raw.get("uniqueStage")),
            substages=[SessionStage.from_api(sub) for sub in raw.get("substages", [])]
        )

@dataclass(frozen=True)
class SessionStage(BaseModel):
    id: str
    slug: str
    name: str
    year: str
    start: str
    end: str
    kind: str # e.g. "Race", "Sprint", "Qualifying", "Practice"
    status: Optional[Status] = None
    circuit: Optional[Circuit] = None
    country: Optional[Country] = None
    description: Optional[str] = None
    unique_stage: Optional[UniqueStage] = None

    @classmethod
    def _from_api(cls, raw: dict) -> SessionStage:
        return SessionStage(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            year=raw.get("year"),
            start=timestamp_to_iso(raw.get("startDateTimestamp")),
            end=timestamp_to_iso(raw.get("endDateTimestamp")),
            kind=raw.get("type", {}).get("name"),
            status=Status.from_api(raw.get("status")),
            circuit=Circuit.from_api(raw.get("info")),
            country=Country.from_api(raw.get("country")),
            description=raw.get("description"),
            unique_stage=UniqueStage.from_api(raw.get("uniqueStage"))
        )
