from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .core import BaseModel, Coordinates, Country
from .team import Team


@dataclass(frozen=True)
class Stadium(BaseModel):
    name: str
    capacity: int

    @classmethod
    def _from_api(cls, raw: dict) -> Stadium:
        return Stadium(
            name=raw.get("name"),
            capacity=raw.get("capacity"),
        )

@dataclass(frozen=True)
class Venue(BaseModel):
    id: str
    slug: str
    name: str
    capacity: int
    city: str
    stadium: Stadium
    country: Country
    coordinates: Coordinates

# Note - Additional keys:
# - mainTeams (issue is circular dependency with Team, didn't want to bother for now)
