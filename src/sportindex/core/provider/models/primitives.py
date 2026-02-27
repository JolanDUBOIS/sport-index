from __future__ import annotations

from typing import Generic, TypeVar

from sportindex.core.base import BaseModel


# =====================================================================
# Basic reusable blocks
# =====================================================================

class Timestamp(int):
    """Marker type for timestamp fields."""
    pass


class ISODate(str):
    """Marker type for ISO-formatted datetime strings."""
    pass


class RawAmount(BaseModel):
    """Monetary amount (transfer fees, salaries, prize money)."""
    value: float
    currency: str  # e.g. "EUR", "USD"


class RawStatus(BaseModel):
    code: int
    type: str         # e.g. "finished", "inprogress", "notstarted"
    description: str


class RawCoordinates(BaseModel):
    latitude: float
    longitude: float


class RawPerformance(BaseModel):
    total: int
    wins: int
    draws: int
    losses: int
    goalScored: int
    goalConceded: int
    totalPoints: int


# =====================================================================
# Channel / TV
# =====================================================================

class RawChannel(BaseModel):
    id: int              # ASSUMPTION: int — could be str
    name: str
