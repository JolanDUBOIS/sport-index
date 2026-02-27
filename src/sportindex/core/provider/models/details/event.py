from __future__ import annotations

from ..entities import RawPlayer
from sportindex.core.base import BaseModel


# =====================================================================
# Lineups
# =====================================================================

class RawLineup(BaseModel):
    players: list[RawPlayer]
    missingPlayers: list[RawPlayer]
    formation: str                  # e.g. "4-3-3"


# =====================================================================
# Event Statistics
# =====================================================================

class RawStatisticsItem(BaseModel):
    key: str                      # e.g. "ballPossession", "totalShots"
    name: str                     # Display name, e.g. "Ball possession"
    home: str                     # String representation, e.g. "54%"
    away: str
    compareCode: int              # 1=home better, 2=away better, 3=tied
    statisticsType: str           # "positive" or "negative"
    # REMARK: API also returns `valueType`, `homeValue`, `awayValue`,
    # `renderType` — not typed here, but accessible on the dict.
    homeValue: int | float
    awayValue: int | float
    valueType: str
    renderType: int


class RawStatisticsGroup(BaseModel):
    groupName: str                    # e.g. "Match overview", "Shots"
    statisticsItems: list[RawStatisticsItem]


class RawPeriodStatistics(BaseModel):
    period: str                       # e.g. "ALL", "1ST", "2ND"
    groups: list[RawStatisticsGroup]


# =====================================================================
# Momentum Graph
# =====================================================================

class RawMomentumPoint(BaseModel):
    minute: float
    value: int  # positive=home, negative=away, range ~[-100, 100]


# =====================================================================
# Incidents
# =====================================================================

class RawIncident(BaseModel):
        """TODO - We voluntarily keep the raw incident dict as-is, and only parse out a few key fields for easier handling in the higher layers."""
        incidentType: str
        id: int
        time: int
