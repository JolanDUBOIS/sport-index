from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Type, TypeVar


# === Base Model ===

T = TypeVar("T", bound="BaseModel")

@dataclass(frozen=True)
class BaseModel:
    @classmethod
    def from_api(cls: Type[T], raw: dict | None) -> T | None:
        if raw is None:
            return None
        return cls._from_api(raw)

    @classmethod
    def _from_api(cls: Type[T], raw: dict) -> T:
        raise NotImplementedError

    def to_dict(self) -> dict:
        return asdict(self)


# === Basic Utility Models ===

@dataclass(frozen=True)
class Score:
    home: int
    away: int

@dataclass(frozen=True)
class Status(BaseModel):
    code: int
    type: str
    description: str

    @classmethod
    def _from_api(cls, raw: dict) -> Status:
        return Status(
            code=raw.get("code"),
            type=raw.get("type"),
            description=raw.get("description"),
        )

@dataclass(frozen=True)
class Amount(BaseModel):
    value: float
    currency: str

    @classmethod
    def _from_api(cls, raw: dict) -> Amount:
        return Amount(
            value=raw.get("value"),
            currency=raw.get("currency"),
        )
    
@dataclass(frozen=True)
class Coordinates(BaseModel):
    latitude: float
    longitude: float

    @classmethod
    def _from_api(cls, raw: dict) -> Coordinates:
        return Coordinates(
            latitude=raw.get("latitude"),
            longitude=raw.get("longitude"),
        )

@dataclass(frozen=True)
class Performance(BaseModel):
    total: int
    wins: int
    draws: int
    losses: int
    goal_scored: int
    goal_conceded: int
    total_points: int

    @classmethod
    def _from_api(cls, raw: dict) -> Performance:
        return Performance(
            total=raw.get("total"),
            wins=raw.get("wins"),
            draws=raw.get("draws"),
            losses=raw.get("losses"),
            goal_scored=raw.get("goalScored"),
            goal_conceded=raw.get("goalConceded"),
            total_points=raw.get("totalPoints"),
        )


# === Core Models ===

@dataclass(frozen=True)
class Country(BaseModel):
    name: str
    slug: str
    alpha2: str
    alpha3: str | None = None
    flag: str | None = None

    @property
    def id(self) -> str:
        return self.alpha2

    @classmethod
    def _from_api(cls, raw: dict) -> Country:
        return Country(
            name=raw.get("name"),
            slug=raw.get("slug"),
            alpha2=raw.get("alpha2"),
            alpha3=raw.get("alpha3"),
            flag=raw.get("flag"),
        )

@dataclass(frozen=True)
class Sport(BaseModel):
    id: str
    slug: str
    name: str

    @classmethod
    def _from_api(cls, raw: dict) -> Sport:
        return Sport(
            id=raw.get("id"),
            name=raw.get("name"),
            slug=raw.get("slug"),
        )
