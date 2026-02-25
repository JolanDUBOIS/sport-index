"""
API response envelope types.

These dataclasses represent the *shapes returned by specific API endpoints*,
as opposed to the domain entity types defined in sibling modules.  They
typically bundle one or more entity types together with pagination flags or
other metadata that only exists at the response level.

See __init__.py for full package docstring and conventions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import RawModel

if TYPE_CHECKING:
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

class RawTeamResponse(RawModel):
    """Response from /team/{id}."""
    team: RawTeam
    relatedTeams: list[RawTeam]
    drivers: list[RawTeam]


# =====================================================================
# Tournament
# =====================================================================

class RawUniqueTournamentSeasonsResponse(RawModel):
    """Response from team/player/manager seasons endpoints."""
    uniqueTournament: RawUniqueTournament
    seasons: list[RawSeason]


# =====================================================================
# Event
# =====================================================================

class RawEventsResponse(RawModel):
    """Response from paginated event list endpoints."""
    events: list[RawEvent]
    hasNextPage: bool


# =====================================================================
# Leaderboard
# =====================================================================

class RawRankingsResponse(RawModel):
    """Response from /rankings/{id}."""
    rankingType: RawRankingType
    rankingRows: list[RawRankingEntry]


# =====================================================================
# Channel / TV
# =====================================================================

class RawChannelScheduleResponse(RawModel):
    """Response from /tv/channel/{id}/schedule."""
    channel: RawChannel
    events: list[RawEvent]
    stages: list[RawStage]


class RawCountryChannelsResponse(RawModel):
    """Response from /tv/event/{id}/country-channels."""
    channels: dict[str, list[int]]


# =====================================================================
# Event Details
# =====================================================================

class RawLineupsResponse(RawModel):
    """Response from /event/{id}/lineups."""
    home: RawLineup
    away: RawLineup


class RawEventStatisticsResponse(RawModel):
    """Response from /event/{id}/statistics."""
    statistics: list[RawPeriodStatistics]


class RawMomentumGraphResponse(RawModel):
    """Response from /event/{id}/graph."""
    graphPoints: list[RawMomentumPoint]
    periodTime: int
    periodCount: int
    overtimeLength: int
