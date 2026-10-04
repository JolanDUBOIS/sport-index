import logging

from .base import BaseSchema
from .channel import _ChannelData
from .core import _CategoryData, _CountryData, _SportData
from .event import (
    MatchPeriod,
    Round,
    _EventData,
    _EventTeamData,
    _FightExtraData,
    _PeriodsData,
    _RacketExtraData,
)
from .incidents import (
    CardIncident,
    ExtraTimeIncident,
    GoalIncident,
    Incident,
    PenaltyIncident,
    PenaltyShootoutIncident,
    PeriodIncident,
    SubstitutionIncident,
    VarDecisionIncident,
)
from .leaderboard import (
    _RacingStandingsData,
    _RacingStandingsEntryData,
    _RankingEntryData,
    _RankingTypeData,
    _TeamStandingsData,
    _TeamStandingsEntryData,
)
from .lineup import Lineup
from .manager import ManagerTenure, _ManagerData
from .player import PlayerPreviousTeam, TeamPlayers, _PlayerData
from .primitives import Amount, EventStatus, Performance, Promotion, Score
from .referee import _RefereeData
from .responses import (
    _ChannelEventVotesResponse,
    _ChannelScheduleResponse,
    _CountryChannelsResponse,
    _EventsResponse,
    _EventStatisticsResponse,
    _LineupsResponse,
    _MomentumGraphResponse,
    _NearEventsResponse,
    _RankingsResponse,
    _SeasonRoundsResponse,
    _TeamResponse,
    _UniqueTournamentSeasonsResponse,
)
from .search import _SearchResultData
from .stage import (
    StageTier,
    _StageData,
    _StageInfoData,
    _StageParentData,
    _UniqueStageData,
)
from .stats_event import MomentumPoint, PeriodStats, StatEntry, StatGroup
from .stats_player import PlayerSeasonStats, PlayerSeasonStatsItem
from .stats_racing import (
    DriverCareerHistory,
    DriverPerformance,
    Lap,
    RaceResults,
    SeasonCareerHistory,
    TotalCareerHistory,
)
from .stats_team import TeamSeasonStats, TeamYearSurfaceStats
from .team import _PlayerTeamInfoData, _TeamData
from .tournament import _SeasonData, _TournamentData, _UniqueTournamentData
from .venue import (
    VenueStatistics,
    _CityData,
    _CoordinatesData,
    _StadiumData,
    _VenueData,
)

logger = logging.getLogger(__name__)


_shared_namespace = dict(locals())

# Primitives
Amount.model_rebuild()
EventStatus.model_rebuild()
Performance.model_rebuild()
Score.model_rebuild()
_CountryData.model_rebuild(_types_namespace=_shared_namespace)
_SportData.model_rebuild(_types_namespace=_shared_namespace)
_CategoryData.model_rebuild(_types_namespace=_shared_namespace)

# Independent Entities
_ManagerData.model_rebuild(_types_namespace=_shared_namespace)
_RefereeData.model_rebuild(_types_namespace=_shared_namespace)
_VenueData.model_rebuild(_types_namespace=_shared_namespace)

# Interdependent Entities
_TeamData.model_rebuild(_types_namespace=_shared_namespace)
_PlayerData.model_rebuild(_types_namespace=_shared_namespace)

# Tournaments & Stages
_SeasonData.model_rebuild(_types_namespace=_shared_namespace)
_TournamentData.model_rebuild(_types_namespace=_shared_namespace)
_UniqueTournamentData.model_rebuild(_types_namespace=_shared_namespace)
_StageData.model_rebuild(_types_namespace=_shared_namespace)
_UniqueStageData.model_rebuild(_types_namespace=_shared_namespace)

# Events & Responses
_EventData.model_rebuild(_types_namespace=_shared_namespace)
_SearchResultData.model_rebuild(_types_namespace=_shared_namespace)
TeamPlayers.model_rebuild(_types_namespace=_shared_namespace)
_EventsResponse.model_rebuild(_types_namespace=_shared_namespace)
_NearEventsResponse.model_rebuild(_types_namespace=_shared_namespace)
_UniqueTournamentSeasonsResponse.model_rebuild(_types_namespace=_shared_namespace)
_SeasonRoundsResponse.model_rebuild(_types_namespace=_shared_namespace)

# Standings & Stats
_TeamStandingsData.model_rebuild(_types_namespace=_shared_namespace)
_TeamResponse.model_rebuild(_types_namespace=_shared_namespace)
_RacingStandingsEntryData.model_rebuild(_types_namespace=_shared_namespace)
_RacingStandingsData.model_rebuild(_types_namespace=_shared_namespace)
RaceResults.model_rebuild(_types_namespace=_shared_namespace)
PeriodStats.model_rebuild(_types_namespace=_shared_namespace)
_EventStatisticsResponse.model_rebuild(_types_namespace=_shared_namespace)
PlayerSeasonStats.model_rebuild(_types_namespace=_shared_namespace)
ManagerTenure.model_rebuild(_types_namespace=_shared_namespace)
MomentumPoint.model_rebuild(_types_namespace=_shared_namespace)
_MomentumGraphResponse.model_rebuild(_types_namespace=_shared_namespace)

# Incidents
GoalIncident.model_rebuild(_types_namespace=_shared_namespace)
PenaltyIncident.model_rebuild(_types_namespace=_shared_namespace)
PenaltyShootoutIncident.model_rebuild(_types_namespace=_shared_namespace)
CardIncident.model_rebuild(_types_namespace=_shared_namespace)
PeriodIncident.model_rebuild(_types_namespace=_shared_namespace)
VarDecisionIncident.model_rebuild(_types_namespace=_shared_namespace)
SubstitutionIncident.model_rebuild(_types_namespace=_shared_namespace)
ExtraTimeIncident.model_rebuild(_types_namespace=_shared_namespace)

# Misc Responses
_LineupsResponse.model_rebuild(_types_namespace=_shared_namespace)
_RankingsResponse.model_rebuild(_types_namespace=_shared_namespace)
_ChannelScheduleResponse.model_rebuild(_types_namespace=_shared_namespace)
Lineup.model_rebuild(_types_namespace=_shared_namespace)
_RankingTypeData.model_rebuild(_types_namespace=_shared_namespace)
_ChannelData.model_rebuild(_types_namespace=_shared_namespace)

# Clean up
del _shared_namespace

__all__ = [
    "BaseSchema",
    "_ChannelData",
    "_SportData",
    "_CountryData",
    "_CategoryData",
    "Round",
    "MatchPeriod",
    "_PeriodsData",
    "_FightExtraData",
    "_RacketExtraData",
    "_EventTeamData",
    "_EventData",
    "Incident",
    "GoalIncident",
    "PenaltyIncident",
    "PenaltyShootoutIncident",
    "CardIncident",
    "PeriodIncident",
    "VarDecisionIncident",
    "SubstitutionIncident",
    "ExtraTimeIncident",
    "_TeamStandingsEntryData",
    "_TeamStandingsData",
    "_RacingStandingsEntryData",
    "_RankingTypeData",
    "_RankingEntryData",
    "Lineup",
    "_ManagerData",
    "ManagerTenure",
    "_PlayerData",
    "PlayerPreviousTeam",
    "TeamPlayers",
    "Amount",
    "EventStatus",
    "Performance",
    "Promotion",
    "Score",
    "_RefereeData",
    "_TeamResponse",
    "_UniqueTournamentSeasonsResponse",
    "_SeasonRoundsResponse",
    "_EventsResponse",
    "_NearEventsResponse",
    "_RankingsResponse",
    "_ChannelScheduleResponse",
    "_CountryChannelsResponse",
    "_ChannelEventVotesResponse",
    "_LineupsResponse",
    "_EventStatisticsResponse",
    "_MomentumGraphResponse",
    "_SearchResultData",
    "StageTier",
    "_StageInfoData",
    "_StageParentData",
    "_UniqueStageData",
    "_StageData",
    "StatEntry",
    "StatGroup",
    "PeriodStats",
    "MomentumPoint",
    "PlayerSeasonStatsItem",
    "PlayerSeasonStats",
    "RaceResults",
    "SeasonCareerHistory",
    "TotalCareerHistory",
    "DriverCareerHistory",
    "Lap",
    "DriverPerformance",
    "TeamSeasonStats",
    "TeamYearSurfaceStats",
    "_PlayerTeamInfoData",
    "_TeamData",
    "_SeasonData",
    "_UniqueTournamentData",
    "_TournamentData",
    "_CoordinatesData",
    "_CityData",
    "_StadiumData",
    "_VenueData",
    "VenueStatistics",
]
