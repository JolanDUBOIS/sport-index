from .base import BaseSchema


class Amount(BaseSchema):
    value: float
    currency: str  # e.g. "EUR", "USD"


class EventStatus(BaseSchema):
    code: int | None = None
    type: str         # e.g. "finished", "inprogress", "notstarted"
    description: str | None = None


class Performance(BaseSchema):
    total: int | None = None
    wins: int | None = None
    draws: int | None = None
    losses: int | None = None
    goal_scored: int | None = None
    goal_conceded: int | None = None
    total_points: int | None = None


class Promotion(BaseSchema):
    id: int
    text: str  # Display name, e.g. "Champions League"


class Score(BaseSchema):
    home: int
    away: int