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


class TennisPoint(BaseSchema):
    home_point: str                           # Game score once the point is played: "0", "15", "30", "40", "A"
    away_point: str
    point_description: int | None = None      # Provider code, undocumented
    home_point_type: int | None = None        # Provider code, undocumented
    away_point_type: int | None = None        # Provider code, undocumented


class TennisGameScore(BaseSchema):
    home_score: int                           # Games won in the set once this game ends
    away_score: int
    serving: int | None = None                # 1=home served, 2=away served
    scoring: int | None = None                # 1=home won the game, 2=away won it


class TennisGame(BaseSchema):
    number: int = Field(alias="game")         # Position in the set, from 1
    points: list[TennisPoint] = Field(default_factory=list)  # The game-winning point is not listed
    score: TennisGameScore | None = None


class TennisSet(BaseSchema):
    number: int = Field(alias="set")          # Position in the match, from 1
    games: list[TennisGame] = Field(default_factory=list)
