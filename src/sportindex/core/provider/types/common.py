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
    alpha2: str
    alpha3: str
    flag: str


class RawCategory(TypedDict, total=False):
    id: int
    name: str
    slug: str
    sport: RawSport
    alpha2: str
    flag: str
    country: RawCountry
