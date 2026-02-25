"""
Core and common dataclass types shared across all other type modules.

See __init__.py for full package docstring and conventions.
"""

from __future__ import annotations

from .base import RawModel


# =====================================================================
# Core
# =====================================================================

class RawSport(RawModel):
    id: int
    name: str
    slug: str


class RawCountry(RawModel):
    name: str
    slug: str
    alpha2: str
    alpha3: str
    flag: str


class RawCategory(RawModel):
    id: int
    name: str
    slug: str
    sport: RawSport
    alpha2: str
    flag: str
    country: RawCountry
