from __future__ import annotations

from typing import TypedDict


# =====================================================================
# Basic reusable blocks
# =====================================================================

class Timestamp(int):
    """Marker type for timestamp fields."""
    pass


class ISODate(str):
    """Marker type for ISO-formatted datetime strings."""
    pass


class RawAmount(TypedDict, total=False):
    """Monetary amount (transfer fees, salaries, prize money)."""
    value: float
    currency: str  # e.g. "EUR", "USD"


class RawStatus(TypedDict, total=False):
    code: int
    type: str         # e.g. "finished", "inprogress", "notstarted"
    description: str


class RawCoordinates(TypedDict, total=False):
    latitude: float
    longitude: float


class RawCity(TypedDict, total=False):
    name: str


class RawPerformance(TypedDict, total=False):
    total: int
    wins: int
    draws: int
    losses: int
    goalScored: int
    goalConceded: int
    totalPoints: int


class RawPromotion(TypedDict, total=False):
    id: int
    text: str  # Display name, e.g. "Champions League"


# =====================================================================
# Channel / TV
# =====================================================================

class RawChannel(TypedDict, total=False):
    id: int
    name: str
