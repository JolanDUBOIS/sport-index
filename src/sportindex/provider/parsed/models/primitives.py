from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import BaseParsedModel
if TYPE_CHECKING:
    from sportindex.provider.raw.models import RawAmount, RawChannel, RawPerformance


@dataclass
class ParsedAmount(BaseParsedModel):
    value: float
    currency: str

    @classmethod
    def _parse(cls, raw: RawAmount) -> ParsedAmount:
        return cls(**raw)


@dataclass
class ParsedChannel(BaseParsedModel):
    id: int
    name: str

    @classmethod
    def _parse(cls, raw: RawChannel) -> ParsedChannel:
        return cls(**raw)


@dataclass
class ParsedPerformance(BaseParsedModel):
    total: int
    wins: int
    draws: int
    losses: int
    goalScored: int
    goalConceded: int
    totalPoints: int

    @classmethod
    def _parse(cls, raw: RawPerformance) -> ParsedPerformance:
        return cls(**raw)
