from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import BaseParsedModel
if TYPE_CHECKING:
    from sportindex.provider.raw.models import RawAmount, RawChannel, RawPerformance


@dataclass
class Amount(BaseParsedModel):
    value: float
    currency: str

    @classmethod
    def _parse(cls, raw: RawAmount) -> Amount:
        return cls(**raw)


@dataclass
class Channel(BaseParsedModel):
    id: int
    name: str

    @classmethod
    def _parse(cls, raw: RawChannel) -> Channel:
        return cls(**raw)


@dataclass
class Performance(BaseParsedModel):
    total: int
    wins: int
    draws: int
    losses: int
    goalScored: int
    goalConceded: int
    totalPoints: int

    @classmethod
    def _parse(cls, raw: RawPerformance) -> Performance:
        return cls(**raw)
