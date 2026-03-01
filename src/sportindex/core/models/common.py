"""
Core and common dataclass types shared across all other type modules.

See __init__.py for full package docstring and conventions.
"""

from __future__ import annotations

from .base import BaseModel


# =====================================================================
# Core
# =====================================================================

class Sport(BaseModel):
    id: int
    name: str
    slug: str


class Country(BaseModel):
    name: str
    slug: str
    alpha2: str
    alpha3: str
    flag: str


class Category(BaseModel):
    id: int
    name: str
    slug: str
    sport: Sport
    alpha2: str
    flag: str
    country: Country
