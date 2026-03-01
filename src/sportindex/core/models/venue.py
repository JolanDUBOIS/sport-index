from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseModel, RawModel, ParsedModel
from .common import Country
from .primitives import Coordinates, City

if TYPE_CHECKING:
    from .team import RawTeam, ParsedTeam


# =====================================================================
# Venue
# =====================================================================

class Venue(BaseModel):
    id: int
    slug: str
    name: str
    capacity: int
    city: City
    stadium: Stadium
    country: Country
    venueCoordinates: Coordinates

class RawVenue(Venue, RawModel):
    mainTeams: list[RawTeam]

class ParsedVenue(Venue, ParsedModel):
    mainTeams: list[ParsedTeam]


# =====================================================================
# Stadium
# =====================================================================

class Stadium(BaseModel):
    name: str
    capacity: int
