"""
TODO
"""

from __future__ import annotations

from typing import TypedDict, Any


# =====================================================================
# Basic reusable blocks
# =====================================================================

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


class RawPerformance(TypedDict, total=False):
    total: int
    wins: int
    draws: int
    losses: int
    goalScored: int
    goalConceded: int
    totalPoints: int


# =====================================================================
# Search Results
# =====================================================================

class RawSearchResult(TypedDict, total=False):
    """A single search result.
    The ``entity`` is a raw dict whose shape depends on ``type``:
      - "team"             → RawTeam
      - "player"           → RawPlayer
      - "manager"          → RawManager
      - "referee"          → RawReferee
      - "uniqueTournament" → RawUniqueTournament
      - "venue"            → RawVenue
    """
    type: str                 # The entity type
    entity: dict[str, Any]    # Shape depends on `type`
    score: float              # Search relevance score


# =====================================================================
# Channel / TV
# =====================================================================

class RawChannel(TypedDict, total=False):
    id: int              # ASSUMPTION: int — could be str
    name: str



