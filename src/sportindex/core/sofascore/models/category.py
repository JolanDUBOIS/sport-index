from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass

from .core import BaseModel, Country, Sport


@dataclass(frozen=True)
class TransferWindow(BaseModel):
    start: str
    end: str

    @classmethod
    def _from_api(cls, raw: dict) -> TransferWindow:
        return TransferWindow(
            start=raw.get("activeFrom"),
            end=raw.get("activeTo"),
        )

@dataclass(frozen=True)
class Category(BaseModel):
    id: str
    slug: str
    name: str
    sport: Sport
    country: Optional[Country] = None
    transfer_periods: Optional[List[TransferWindow]] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Category:
        return Category(
            id=raw.get("id"),
            name=raw.get("name"),
            slug=raw.get("slug"),
            sport=Sport.from_api(raw.get("sport")),
            country=Country.from_api(raw.get("country")),
            transfer_periods=[TransferWindow.from_api(tp) for tp in raw.get("transferPeriod", [])],
        )
