"""
API response envelope types.

These TypedDicts represent the *shapes returned by specific API endpoints*,
as opposed to the domain entity types defined in sibling modules.  They
typically bundle one or more entity types together with pagination flags or
other metadata that only exists at the response level.

See __init__.py for full package docstring and conventions.
"""

from __future__ import annotations

from typing import TypedDict

from .tournament import RawSeason, RawUniqueTournament
from .entities import RawTeam
from .event import RawEvent
from .stages import RawStage
from .primitives import RawChannel
from .leaderboard import RawRankingEntry, RawRankingType
from .details.event import RawLineup, RawMomentumPoint, RawPeriodStatistics


# =====================================================================
# Team
# =====================================================================

class RawTeamResponse(TypedDict, total=False):
    """Response from /team/{id}."""
    team: RawTeam
    relatedTeams: list[RawTeam]
    drivers: list[RawTeam]


# =====================================================================
# Tournament
# =====================================================================

class RawUniqueTournamentSeasonsResponse(TypedDict, total=False):
    """Response from team/player/manager seasons endpoints."""
    uniqueTournament: RawUniqueTournament
    seasons: list[RawSeason]


# =====================================================================
# Event
# =====================================================================

class RawEventsResponse(TypedDict, total=False):
    """Response from paginated event list endpoints."""
    events: list[RawEvent]
    hasNextPage: bool


# =====================================================================
# Leaderboard
# =====================================================================

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

class RawChannelScheduleResponse(TypedDict, total=False):
    """Response from /tv/channel/{id}/schedule."""
    channel: RawChannel
    events: list[RawEvent]
    stages: list[RawStage]


class RawCountryChannelsResponse(TypedDict, total=False):
    """Response from /tv/event/{id}/country-channels.
    The ``channels`` key maps country codes to lists of channel IDs.
    """
    channels: dict[str, list[int]]


# =====================================================================
# Event Details
# =====================================================================

class RawLineupsResponse(TypedDict, total=False):
    """Response from /event/{id}/lineups.
    REMARK: The actual response nests this under a ``lineups`` key which
    the provider already extracts for you.
    """
    home: RawLineup
    away: RawLineup


class RawEventStatisticsResponse(TypedDict, total=False):
    """Response from /event/{id}/statistics."""
    statistics: list[RawPeriodStatistics]


class RawMomentumGraphResponse(TypedDict, total=False):
    """Response from /event/{id}/graph."""
    graphPoints: list[RawMomentumPoint]
    periodTime: int
    periodCount: int
    overtimeLength: int
