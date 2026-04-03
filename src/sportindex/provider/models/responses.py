from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

from .base import BaseSchema

if TYPE_CHECKING:
    from .channel import _ChannelData
    from .event import _EventData, Round
    from .leaderboard import _RankingEntryData, _RankingTypeData
    from .lineup import Lineup
    from .stage import _StageData
    from .stats_event import PeriodStats, MomentumPoint
    from .team import _TeamData
    from .tournament import _SeasonData, _UniqueTournamentData


# =====================================================================
# Team
# =====================================================================

class _TeamResponse(BaseSchema):
    team: _TeamData
    related_teams: list[_TeamData] = Field(default_factory=list)
    drivers: list[_TeamData] = Field(default_factory=list)


# =====================================================================
# Tournament
# =====================================================================

class _UniqueTournamentSeasonsResponse(BaseSchema):
    unique_tournament: _UniqueTournamentData
    seasons: list[_SeasonData] = Field(default_factory=list)


class _SeasonRoundsResponse(BaseSchema):
    current_round: Round | None = None
    rounds: list[Round] = Field(default_factory=list)


# =====================================================================
# Event
# =====================================================================

class _EventsResponse(BaseSchema):
    has_next_page: bool = False
    events: list[_EventData] = Field(default_factory=list)


# =====================================================================
# Leaderboard
# =====================================================================

class _RankingsResponse(BaseSchema):
    ranking_type: _RankingTypeData
    ranking_rows: list[_RankingEntryData] = Field(default_factory=list)


# =====================================================================
# Channel / TV
# =====================================================================

class _ChannelScheduleResponse(BaseSchema):
    channel: _ChannelData
    events: list[_EventData] = Field(default_factory=list)
    stages: list[_StageData] = Field(default_factory=list)


class _CountryChannelsResponse(BaseSchema):
    channels: dict[str, list[int]] = Field(default_factory=dict)


class _ChannelEventVotesResponse(BaseSchema):
    channel: _ChannelData
    upvotes: int = 0
    downvotes: int = 0


# =====================================================================
# Event Details
# =====================================================================

class _LineupsResponse(BaseSchema):
    home: Lineup | None = None
    away: Lineup | None = None


class _EventStatisticsResponse(BaseSchema):
    statistics: list[PeriodStats] = Field(default_factory=list)


class _MomentumGraphResponse(BaseSchema):
    points: list[MomentumPoint] = Field(default_factory=list)
    period_time: int = 0
    period_count: int = 0
    overtime_length: int = 0
