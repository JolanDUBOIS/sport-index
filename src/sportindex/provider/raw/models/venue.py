from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from .core import Country
    from .primitives import Coordinates, City
    from .team import Team


# =====================================================================
# Stadium
# =====================================================================

class Stadium(TypedDict, total=False):
    name: str
    capacity: int


# =====================================================================
# Venue
# =====================================================================

class Venue(TypedDict, total=False):
    id: int
    slug: str
    name: str
    capacity: int
    city: City
    stadium: Stadium
    country: Country
    venueCoordinates: Coordinates
    mainTeams: list[Team]
