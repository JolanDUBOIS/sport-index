from __future__ import annotations

from dataclasses import dataclass

from .base import BaseParsedModel
from sportindex.provider.raw import RawAmount, RawChannel, RawPerformance, RawPromotion


@dataclass
class ParsedAmount(BaseParsedModel):
    __annotations__ = RawAmount.__annotations__


@dataclass
class ParsedChannel(BaseParsedModel):
    __annotations__ = RawChannel.__annotations__


@dataclass
class ParsedPerformance(BaseParsedModel):
    __annotations__ = RawPerformance.__annotations__


@dataclass
class ParsedPromotion(BaseParsedModel):
    __annotations__ = RawPromotion.__annotations__
