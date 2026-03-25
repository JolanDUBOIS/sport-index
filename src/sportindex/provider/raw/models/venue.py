from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from .core import RawCountry
    from .primitives import RawCoordinates, RawCity
    from .team import RawTeam


# =====================================================================
# Stadium
# =====================================================================

class RawStadium(TypedDict, total=False):
    name: str
    capacity: int


# =====================================================================
# Venue
# =====================================================================

class RawVenue(TypedDict, total=False):
    id: int
    slug: str
    name: str
    capacity: int
    city: RawCity
    stadium: RawStadium
    country: RawCountry
    venueCoordinates: RawCoordinates
    mainTeams: list[RawTeam]
