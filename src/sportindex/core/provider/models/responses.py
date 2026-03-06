from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from .details import Lineup, MomentumPoint, PeriodStatistics
    from .event import Event
    from .leaderboard import RankingEntry, RankingType
    from .primitives import Channel
    from .stage import Stage
    from .team import Team
    from .tournament import Season, UniqueTournament


# =====================================================================
# Team
# =====================================================================

class TeamResponse(TypedDict, total=False):
    team: Team
    relatedTeams: list[Team]
    drivers: list[Team]


# =====================================================================
# Tournament
# =====================================================================

class UniqueTournamentSeasonsResponse(TypedDict, total=False):
    uniqueTournament: UniqueTournament
    seasons: list[Season]


# =====================================================================
# Event
# =====================================================================

class EventsResponse(TypedDict, total=False):
    hasNextPage: bool
    events: list[Event]


# =====================================================================
# Leaderboard
# =====================================================================

class RankingsResponse(TypedDict, total=False):
    rankingType: RankingType
    rankingRows: list[RankingEntry]


# =====================================================================
# Channel / TV
# =====================================================================

class ChannelScheduleResponse(TypedDict, total=False):
    channel: Channel
    events: list[Event]
    stages: list[Stage]


class CountryChannelsResponse(TypedDict, total=False):
    channels: dict[str, list[int]]


# =====================================================================
# Event Details
# =====================================================================

class LineupsResponse(TypedDict, total=False):
    home: Lineup
    away: Lineup


class EventStatisticsResponse(TypedDict, total=False):
    statistics: list[PeriodStatistics]


class MomentumGraphResponse(TypedDict, total=False):
    graphPoints: list[MomentumPoint]
    periodTime: int
    periodCount: int
    overtimeLength: int
