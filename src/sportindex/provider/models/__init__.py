import logging
logger = logging.getLogger(__name__)

from .base import BaseSchema
from .channel import _ChannelData
from .core import _SportData, _CountryData, _CategoryData
from .event import Round, MatchPeriod, _PeriodsData, _FightExtraData, _RacketExtraData, _EventTeamData, _EventData
from .incidents import Incident, GoalIncident, PenaltyIncident, PenaltyShootoutIncident, CardIncident, PeriodIncident, VarDecisionIncident, SubstitutionIncident, ExtraTimeIncident
from .leaderboard import _TeamStandingsEntryData, _TeamStandingsData, _RacingStandingsEntryData, _RankingTypeData, _RankingEntryData
from .lineup import Lineup
from .manager import _ManagerData, ManagerTenure
from .player import _PlayerData, PlayerPreviousTeam, TeamPlayers
from .primitives import Amount, EventStatus, Performance, Promotion, Score
from .referee import _RefereeData
from .responses import _TeamResponse, _UniqueTournamentSeasonsResponse, _SeasonRoundsResponse, _EventsResponse, _RankingsResponse, _ChannelScheduleResponse, _CountryChannelsResponse, _ChannelEventVotesResponse, _LineupsResponse, _EventStatisticsResponse, _MomentumGraphResponse
from .search import _SearchResultData
from .stage import StageTier, _StageInfoData, _StageParentData, _UniqueStageData, _StageData
from .stats_event import StatEntry, StatGroup, PeriodStats, MomentumPoint
from .stats_player import PlayerSeasonStatsItem, PlayerSeasonStats
from .stats_racing import RaceResults, SeasonCareerHistory, TotalCareerHistory, DriverCareerHistory, Lap, DriverPerformance
from .stats_team import TeamSeasonStats, TeamYearSurfaceStats
from .team import _PlayerTeamInfoData, _TeamData
from .tournament import _SeasonData, _UniqueTournamentData, _TournamentData
from .venue import _CoordinatesData, _CityData, _StadiumData, _VenueData, VenueStatistics


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
_UniqueTournamentSeasonsResponse.model_rebuild(_types_namespace=_shared_namespace)
_SeasonRoundsResponse.model_rebuild(_types_namespace=_shared_namespace)

# Standings & Stats
_TeamStandingsData.model_rebuild(_types_namespace=_shared_namespace)
_TeamResponse.model_rebuild(_types_namespace=_shared_namespace)
_RacingStandingsEntryData.model_rebuild(_types_namespace=_shared_namespace)
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