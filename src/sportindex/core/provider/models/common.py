"""
Core and common dataclass types shared across all other type modules.

See __init__.py for full package docstring and conventions.
"""

from __future__ import annotations

from sportindex.core.base import BaseModel


# =====================================================================
# Core
# =====================================================================

class RawSport(BaseModel):
    id: int
    name: str
    slug: str


class RawCountry(BaseModel):
    name: str
    slug: str
    alpha2: str
    alpha3: str
    flag: str


class RawCategory(BaseModel):
    id: int
    name: str
    slug: str
    sport: RawSport
    alpha2: str
    flag: str
    country: RawCountry
