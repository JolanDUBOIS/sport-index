"""
Provider module for translating external API data into domain models.

This module serves as an internal abstraction layer between the data provider APIs
and the domain layer. It contains implementation details and data transformation logic
that should not be directly imported or used by external consumers.

Main exports are intended for internal use only within the sportindex package.
"""

from .fetcher import Fetcher
from .main import SofascoreProvider
from .models import (
    Amount,
    EventStatus,
    MatchPeriod,
    MomentumPoint,
    PeriodStats,
    Promotion,
    Round,
    Score,
    StageTier,
)
from .offline import RecordingFetcher

__all__ = [
    "Fetcher",
    "SofascoreProvider",
    "Amount",
    "Score",
    "Round",
    "MatchPeriod",
    "PeriodStats",
    "MomentumPoint",
    "Promotion",
    "StageTier",
    "EventStatus",
    "RecordingFetcher",
]
