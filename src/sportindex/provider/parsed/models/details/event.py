from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..base import BaseParsedModel
if TYPE_CHECKING:
    from ..player import ParsedPlayer
    from sportindex.provider.raw.models import RawLineup, RawStatisticsItem, RawStatisticsGroup, RawPeriodStatistics, RawMomentumPoint


# =====================================================================
# Lineups
# =====================================================================

@dataclass
class ParsedLineup(BaseParsedModel):
    formation: str
    players: list[ParsedPlayer]
    missingPlayers: list[ParsedPlayer]

    @classmethod
    def _parse(cls, raw: RawLineup) -> ParsedLineup:
        from ..player import ParsedPlayer
        return cls(
            formation=raw.get("formation"),
            players=[ParsedPlayer.from_raw(p) for p in raw.get("players", [])],
            missingPlayers=[ParsedPlayer.from_raw(p) for p in raw.get("missingPlayers", [])]
        )


# =====================================================================
# Event Statistics
# =====================================================================

@dataclass
class ParsedStatisticsItem(BaseParsedModel):
    key: str                      # e.g. "ballPossession", "totalShots"
    name: str                     # Display name, e.g. "Ball possession"
    home: str                     # String representation, e.g. "54%"
    away: str
    compareCode: int              # 1=home better, 2=away better, 3=tied
    statisticsType: str           # "positive" or "negative"
    homeValue: int | float
    awayValue: int | float
    valueType: str
    renderType: int

    @classmethod
    def _parse(cls, raw: RawStatisticsItem) -> ParsedStatisticsItem:
        return cls(
            key=raw.get("key"),
            name=raw.get("name"),
            home=raw.get("home"),
            away=raw.get("away"),
            compareCode=raw.get("compareCode"),
            statisticsType=raw.get("statisticsType"),
            homeValue=raw.get("homeValue"),
            awayValue=raw.get("awayValue"),
            valueType=raw.get("valueType"),
            renderType=raw.get("renderType")
        )


@dataclass
class ParsedStatisticsGroup(BaseParsedModel):
    name: str                    # e.g. "Match overview", "Shots"
    items: list[ParsedStatisticsItem]

    @classmethod
    def _parse(cls, raw: RawStatisticsGroup) -> ParsedStatisticsGroup:
        return cls(
            name=raw.get("groupName"),
            items=[ParsedStatisticsItem._parse(i) for i in raw.get("statisticsItems", [])]
        )


@dataclass
class ParsedPeriodStatistics(BaseParsedModel):
    period: str                       # e.g. "ALL", "1ST", "2ND"
    groups: list[ParsedStatisticsGroup]

    @classmethod
    def _parse(cls, raw: RawPeriodStatistics) -> ParsedPeriodStatistics:
        return cls(
            period=raw.get("period"),
            groups=[ParsedStatisticsGroup._parse(g) for g in raw.get("groups", [])]
        )


# =====================================================================
# Momentum Graph
# =====================================================================

@dataclass
class ParsedMomentumPoint(BaseParsedModel):
    minute: float
    value: int  # positive=home, negative=away, range ~[-100, 100]

    @classmethod
    def _parse(cls, raw: RawMomentumPoint) -> ParsedMomentumPoint:
        return cls(
            minute=raw.get("minute"),
            value=raw.get("value")
        )
