"""
Leaderboard, ranking, channel, search, and transfer TypedDict types.

See __init__.py for full package docstring and conventions.
"""

from __future__ import annotations

from typing import Any, TypedDict

from .common import RawAmount, RawCategory, RawCountry, RawSport, RawStatus
from .entities import RawPlayer, RawTeam, RawTournament, RawUniqueTournament
from .events import RawEvent
from .stages import RawStage


# =====================================================================
# Leaderboard — Team / Individual Standings
# =====================================================================

class RawPromotion(TypedDict, total=False):
    id: int
    text: str  # Display name, e.g. "Champions League"


class RawTeamStandingsEntry(TypedDict, total=False):
    id: int
    team: RawTeam
    position: int
    matches: int
    wins: int
    draws: int
    losses: int
    points: int
    percentage: float          # Win percentage (NBA etc.)
    scoresFor: int
    scoresAgainst: int
    scoreDiffFormatted: str    # e.g. "+15" — ASSUMPTION: always a string
    promotion: RawPromotion
    gamesBehind: int           # ASSUMPTION: int, could be float
    streak: int                # ASSUMPTION: int, could be str


class RawTeamStandings(TypedDict, total=False):
    id: int
    name: str                  # e.g. "Premier League"
    rows: list[RawTeamStandingsEntry]
    tournament: RawTournament
    updatedAtTimestamp: int
    type: str                  # "home", "away", "total"


# =====================================================================
# Leaderboard — Racing Standings
# =====================================================================

class RawRacingStandingsEntry(TypedDict, total=False):
    team: RawTeam
    position: int
    time: str                  # Race time
    interval: str              # Gap to leader
    gap: str                   # Gap to car ahead
    gridPosition: int
    points: int
    updatedAtTimestamp: int
    victories: int
    racesStarted: int
    racesWithPoints: int
    polePositions: int
    podiums: int
    fastestLaps: int
    parentTeam: RawTeam        # Constructor / parent team


# =====================================================================
# Leaderboard — Rankings
# =====================================================================

class RawRankingType(TypedDict, total=False):
    """Nested under the ``rankingType`` key in ranking responses."""
    id: int
    slug: str
    name: str
    gender: str
    sport: RawSport
    category: RawCategory
    uniqueTournament: RawUniqueTournament
    lastUpdatedTimestamp: int


class RawRankingEntry(TypedDict, total=False):
    id: int
    position: int
    team: RawTeam
    points: float
    country: RawCountry
    previousPosition: int
    previousPoints: float
    lastEvent: RawEvent
    updatedTimestamp: int     # ASSUMPTION: same as lastUpdatedTimestamp?


class RawRankingsResponse(TypedDict, total=False):
    """Response from /rankings/{id}.
    REMARK: The current code flattens rankingType into top-level fields.
    In this raw approach, access via data["rankingType"]["id"], etc.
    """
    rankingType: RawRankingType
    rankingRows: list[RawRankingEntry]


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
    channels: dict[str, list[str]]  # ASSUMPTION: channel IDs are strings


# =====================================================================
# Search
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
# Transfer
# =====================================================================

class RawTransfer(TypedDict, total=False):
    id: int
    transferDateTimestamp: int
    player: RawPlayer
    transferFrom: RawTeam
    transferTo: RawTeam
    transferFeeRaw: RawAmount
