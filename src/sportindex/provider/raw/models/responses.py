from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from .details import RawLineup, RawMomentumPoint, RawPeriodStatistics
    from .event import RawEvent
    from .leaderboard import RawRankingEntry, RawRankingType
    from .primitives import RawChannel
    from .stage import RawStage
    from .team import RawTeam
    from .tournament import RawSeason, RawUniqueTournament


# =====================================================================
# Team
# =====================================================================

class RawTeamResponse(TypedDict, total=False):
    team: RawTeam
    relatedTeams: list[RawTeam]
    drivers: list[RawTeam]


# =====================================================================
# Tournament
# =====================================================================

class RawUniqueTournamentSeasonsResponse(TypedDict, total=False):
    uniqueTournament: RawUniqueTournament
    seasons: list[RawSeason]


# =====================================================================
# Event
# =====================================================================

class RawEventsResponse(TypedDict, total=False):
    hasNextPage: bool
    events: list[RawEvent]


# =====================================================================
# Leaderboard
# =====================================================================

class RawRankingsResponse(TypedDict, total=False):
    rankingType: RawRankingType
    rankingRows: list[RawRankingEntry]


# =====================================================================
# Channel / TV
# =====================================================================

class RawChannelScheduleResponse(TypedDict, total=False):
    channel: RawChannel
    events: list[RawEvent]
    stages: list[RawStage]


class RawCountryChannelsResponse(TypedDict, total=False):
    channels: dict[str, list[int]]


class RawChannelEventVotesResponse(TypedDict, total=False):
    tvChannel: RawChannel
    upvote: int
    downvote: int


# =====================================================================
# Event Details
# =====================================================================

class RawLineupsResponse(TypedDict, total=False):
    home: RawLineup
    away: RawLineup


class RawEventStatisticsResponse(TypedDict, total=False):
    statistics: list[RawPeriodStatistics]


class RawMomentumGraphResponse(TypedDict, total=False):
    graphPoints: list[RawMomentumPoint]
    periodTime: int
    periodCount: int
    overtimeLength: int
