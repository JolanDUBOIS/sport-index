"""
Core and common TypedDict types shared across all other type modules.

See __init__.py for full package docstring and conventions.
"""

from __future__ import annotations

from typing import TypedDict


# =====================================================================
# Core
# =====================================================================

class RawSport(TypedDict, total=False):
    id: int
    name: str
    slug: str


class RawCountry(TypedDict, total=False):
    name: str
    slug: str
    alpha2: str   # e.g. "FR" — often used as identifier
    alpha3: str   # e.g. "FRA"
    flag: str     # ASSUMPTION: URL string or null


class RawCategory(TypedDict, total=False):
    id: int
    name: str
    slug: str
    sport: RawSport
    country: RawCountry
    # REMARK: API sometimes includes `transferPeriod`, `uniqueStages`
    # in category responses — not typed here, access via dict keys if needed.


# =====================================================================
# Common
# =====================================================================

class RawStatus(TypedDict, total=False):
    code: int
    type: str         # e.g. "finished", "inprogress", "notstarted"
    description: str  # e.g. "Ended", "1st half"


class RawAmount(TypedDict, total=False):
    """Monetary amount (transfer fees, salaries, prize money)."""
    value: float
    currency: str  # e.g. "EUR", "USD"


class RawTransferWindow(TypedDict, total=False):
    activeFrom: str  # ISO date ASSUMPTION: could be a timestamp instead
    activeTo: str


# =====================================================================
# Venue primitives (no cross-module dependencies)
# =====================================================================

class RawCoordinates(TypedDict, total=False):
    latitude: float
    longitude: float


class RawStadium(TypedDict, total=False):
    name: str
    capacity: int
