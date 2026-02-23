"""
TODO
"""

from __future__ import annotations

from typing import TypedDict, Any

from .event import RawEvent
from .stages import RawStage


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


class RawChannelSchedule(TypedDict, total=False):
    """Response from /tv/channel/{id}/schedule."""
    channel: RawChannel
    events: list[RawEvent]
    stages: list[RawStage]

class RawCountryChannelsResponse(TypedDict, total=False):
    """Response from /tv/event/{id}/country-channels.
    The ``channels`` key maps country codes to lists of channel IDs.
    """
    channels: dict[str, list[int]]
