from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from ..player import Player


# =====================================================================
# Lineups
# =====================================================================

class Lineup(TypedDict, total=False):
    formation: str                  # e.g. "4-3-3"
    players: list[Player]
    missingPlayers: list[Player]


# =====================================================================
# Event Statistics
# =====================================================================

class StatisticsItem(TypedDict, total=False):
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


class StatisticsGroup(TypedDict, total=False):
    groupName: str                    # e.g. "Match overview", "Shots"
    statisticsItems: list[StatisticsItem]


class PeriodStatistics(TypedDict, total=False):
    period: str                       # e.g. "ALL", "1ST", "2ND"
    groups: list[StatisticsGroup]


# =====================================================================
# Momentum Graph
# =====================================================================

class MomentumPoint(TypedDict, total=False):
    minute: float
    value: int  # positive=home, negative=away, range ~[-100, 100]
