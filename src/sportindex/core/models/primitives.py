from __future__ import annotations

from .base import BaseModel


# =====================================================================
# Basic reusable blocks
# =====================================================================

class Timestamp(int):
    """Marker type for timestamp fields."""
    pass


class ISODate(str):
    """Marker type for ISO-formatted datetime strings."""
    pass


class Amount(BaseModel):
    """Monetary amount (transfer fees, salaries, prize money)."""
    value: float
    currency: str  # e.g. "EUR", "USD"


class Status(BaseModel):
    code: int
    type: str         # e.g. "finished", "inprogress", "notstarted"
    description: str


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class City(BaseModel):
    name: str


class Performance(BaseModel):
    total: int
    wins: int
    draws: int
    losses: int
    goalScored: int
    goalConceded: int
    totalPoints: int


class Promotion(BaseModel):
    id: int
    text: str  # Display name, e.g. "Champions League"


# =====================================================================
# Channel / TV
# =====================================================================

class Channel(BaseModel):
    id: int              # ASSUMPTION: int — could be str
    name: str
