from __future__ import annotations

from ..player import RawPlayer, ParsedPlayer
from ..base import BaseModel, RawModel, ParsedModel


# =====================================================================
# Lineups
# =====================================================================

class Lineup(BaseModel):
    formation: str                  # e.g. "4-3-3"

class RawLineup(Lineup, RawModel):
    players: list[RawPlayer]
    missingPlayers: list[RawPlayer]

class ParsedLineup(Lineup, ParsedModel):
    players: list[ParsedPlayer]
    missingPlayers: list[ParsedPlayer]


# =====================================================================
# Event Statistics
# =====================================================================

class StatisticsItem(BaseModel):
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


class StatisticsGroup(BaseModel):
    groupName: str                    # e.g. "Match overview", "Shots"
    statisticsItems: list[StatisticsItem]


class PeriodStatistics(BaseModel):
    period: str                       # e.g. "ALL", "1ST", "2ND"
    groups: list[StatisticsGroup]


# =====================================================================
# Momentum Graph
# =====================================================================

class MomentumPoint(BaseModel):
    minute: float
    value: int  # positive=home, negative=away, range ~[-100, 100]


# =====================================================================
# Incidents
# =====================================================================

class Incident(BaseModel):
        incidentType: str
        id: int
        time: int
