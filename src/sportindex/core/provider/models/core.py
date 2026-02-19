from __future__ import annotations
from dataclasses import dataclass, field
from typing import Type, TypeVar, Optional, Dict, Any


# === Base Model ===

T = TypeVar("T", bound="BaseModel")

@dataclass(frozen=True, kw_only=True)
class BaseModel:
    _raw: Dict[str, Any] = field(
        init=False,
        repr=False,
        compare=False,
    )

    @classmethod
    def from_api(cls: Type[T], raw: Optional[Dict[str, Any]]) -> Optional[T]:
        if not raw:
            return None

        instance = cls._from_api(raw)
        if instance is not None:
            object.__setattr__(instance, "_raw", raw)
        return instance

    @classmethod
    def _from_api(cls: Type[T], raw: Dict[str, Any]) -> T:
        raise NotImplementedError

    def to_dict(self, include_raw: bool = False) -> Dict[str, Any]:
        data = self.__dict__.copy()
        for k, v in data.items():
            if isinstance(v, BaseModel):
                data[k] = v.to_dict()
            elif isinstance(v, list):
                data[k] = [i.to_dict() if isinstance(i, BaseModel) else i for i in v]
            elif isinstance(v, dict):
                data[k] = {key: val.to_dict() if isinstance(val, BaseModel) else val for key, val in v.items()}

        if not include_raw:
            data.pop("_raw", None)
        return data


# === Core Models ===

@dataclass(frozen=True, kw_only=True)
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

@dataclass(frozen=True, kw_only=True)
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

@dataclass(frozen=True, kw_only=True)
class Category(BaseModel):
    id: str
    slug: str
    name: str
    sport: Sport
    country: Optional[Country] = None
    # transferPeriod -> sometimes
    # uniqueStages -> sometimes...

    @classmethod
    def _from_api(cls, raw: dict) -> Category:
        return Category(
            id=raw.get("id"),
            name=raw.get("name"),
            slug=raw.get("slug"),
            sport=Sport.from_api(raw.get("sport")),
            country=Country.from_api(raw.get("country")),
        )
