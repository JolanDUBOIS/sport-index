from __future__ import annotations

from pydantic import Field

from .base import BaseSchema


class StatEntry(BaseSchema):
    key: str                                 # e.g. "ballPossession", "totalShots"
    name: str | None = None                  # Display name, e.g. "Ball possession"
    home: str | None = None                  # String representation, e.g. "54%"
    away: str | None = None
    compare_code: int | None = None           # 1=home better, 2=away better, 3=tied
    statistics_type: str | None = None        # "positive" or "negative"
    home_value: int | float | None = None
    away_value: int | float | None = None
    value_type: str | None = None
    render_type: int | None = None


class StatGroup(BaseSchema):
    name: str | None = None                   # e.g. "Match overview", "Shots"
    items: list[StatEntry] = Field(default_factory=list)


class PeriodStats(BaseSchema):
    period: str                # e.g. "ALL", "1ST", "2ND"
    groups: list[StatGroup] = Field(default_factory=list)


class MomentumPoint(BaseSchema):
    minute: float
    value: int = 0
