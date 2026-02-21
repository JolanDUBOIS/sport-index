from __future__ import annotations
from dataclasses import dataclass

from .core import BaseModel


@dataclass(frozen=True, kw_only=True)
class Score(BaseModel):
    home: int
    away: int

    @classmethod
    def _from_api(cls, raw: dict) -> Score:
        raise NotImplementedError("Score cannot be directly created from API data. It should be constructed within the context of an Event or Period.")

@dataclass(frozen=True, kw_only=True)
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

@dataclass(frozen=True, kw_only=True)
class Amount(BaseModel):
    value: float
    currency: str

    @classmethod
    def _from_api(cls, raw: dict) -> Amount:
        return Amount(
            value=raw.get("value"),
            currency=raw.get("currency"),
        )

@dataclass(frozen=True, kw_only=True)
class TransferWindow(BaseModel):
    start: str
    end: str

    @classmethod
    def _from_api(cls, raw: dict) -> TransferWindow:
        return TransferWindow(
            start=raw.get("activeFrom"),
            end=raw.get("activeTo"),
        )
