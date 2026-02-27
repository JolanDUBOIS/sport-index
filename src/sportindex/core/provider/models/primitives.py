from __future__ import annotations

from typing import Generic, TypeVar

from .base import RawModel


# =====================================================================
# Basic reusable blocks
# =====================================================================

class Timestamp(int):
    """Marker type for timestamp fields."""
    pass


class ISODate(str):
    """Marker type for ISO-formatted datetime strings."""
    pass


class RawAmount(RawModel):
    """Monetary amount (transfer fees, salaries, prize money)."""
    value: float
    currency: str  # e.g. "EUR", "USD"


class RawStatus(RawModel):
    code: int
    type: str         # e.g. "finished", "inprogress", "notstarted"
    description: str


class RawCoordinates(RawModel):
    latitude: float
    longitude: float


class RawPerformance(RawModel):
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

class RawChannel(RawModel):
    id: int              # ASSUMPTION: int — could be str
    name: str
