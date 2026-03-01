from logging import getLogger
logger = getLogger(__name__)
from .base import BaseModel, RawModel, ParsedModel

# Primitives / shared types
from .primitives import (
	Timestamp,
	ISODate,
	Amount,
	Status,
	Coordinates,
	City,
	Performance,
	Promotion,
	Channel,
)

# Common domain types
from .common import (
	Sport,
	Country,
	Category,
)

# Core entities: models that have Raw/Parsed variants
from .team import (
	Team,
	RawTeam,
	ParsedTeam,
	PlayerTeamInfo,
	RawPlayerTeamInfo,
	ParsedPlayerTeamInfo,
)

from .player import (
	Player,
	RawPlayer,
	ParsedPlayer,
)

from .manager import (
	Manager,
	RawManager,
	ParsedManager,
)

from .referee import (
	Referee,
	RawReferee,
	ParsedReferee,
)

from .responses import (
    TeamResponse,
    RawTeamResponse,
    ParsedTeamResponse,
    UniqueTournamentSeasonsResponse,
    RawUniqueTournamentSeasonsResponse,
    ParsedUniqueTournamentSeasonsResponse,
    EventsResponse,
    RawEventsResponse,
    ParsedEventsResponse,
    RankingsResponse,
    RawRankingsResponse,
    ParsedRankingsResponse,
    ChannelScheduleResponse,
    RawChannelScheduleResponse,
    ParsedChannelScheduleResponse,
    CountryChannelsResponse,
    LineupsResponse,
    RawLineupsResponse,
    ParsedLineupsResponse,
    EventStatisticsResponse,
    MomentumGraphResponse,
)

from .venue import (
	Venue,
	RawVenue,
	ParsedVenue,
	Stadium,
)

from .tournament import (
	Season,
	RawSeason,
	ParsedSeason,
	UniqueTournament,
	RawUniqueTournament,
	ParsedUniqueTournament,
	Tournament,
	RawTournament,
	ParsedTournament,
)

from .stage import (
	UniqueStage,
	StageType,
	StageInfo,
	StageParent,
	RawStageParent,
	ParsedStageParent,
	Stage,
	RawStage,
	ParsedStage,
)

from .event import (
	Event,
	RawEvent,
	ParsedEvent,
	Round,
	EventScore,
	EventTime,
	EventPeriodLabels,
)

# Leaderboards / rankings
from .leaderboard import (
	TeamStandingsEntry,
	RawTeamStandingsEntry,
	ParsedTeamStandingsEntry,
	TeamStandings,
	RawTeamStandings,
	ParsedTeamStandings,
	RacingStandingsEntry,
	RawRacingStandingsEntry,
	ParsedRacingStandingsEntry,
    RankingType,
    RawRankingType,
    ParsedRankingType,
	RankingEntry,
	RawRankingEntry,
	ParsedRankingEntry,
)

# Search helpers
from .search import (
	SearchResult,
	RawSearchResult,
	ParsedSearchResult,
)

# Detailed / nested types (re-exported from details.__init__)
from .details import (
	ParsedManagerCareerHistoryItem,
	ParsedPlayerPreviousTeam,
	ParsedPlayerSeasonStats,
	ParsedTeamPlayers,
	PlayerSeasonStatsItem,
	RawManagerCareerHistoryItem,
	RawPlayerPreviousTeam,
	RawPlayerSeasonStats,
	RawTeamPlayers,
	TeamSeasonStats,
	TeamYearStats,
	TeamYearSurfaceStats,
	VenueStatistics,
	Incident,
	MomentumPoint,
	ParsedLineup,
	PeriodStatistics,
	RawLineup,
	StatisticsGroup,
	StatisticsItem,
	Lap,
	DriverCareerHistory,
	DriverPerformance,
	RaceResults,
	SeasonCareerHistory,
	TotalCareerHistory,
	RawDriverCareerHistory,
	RawDriverPerformance,
	RawRaceResults,
	RawSeasonCareerHistory,
	RawTotalCareerHistory,
)

# Public API
__all__ = [
	"logger",
	# base
	"BaseModel",
	"RawModel",
	"ParsedModel",

	# primitives
	"Timestamp",
	"ISODate",
	"Amount",
	"Status",
	"Coordinates",
	"City",
	"Performance",
	"Promotion",
	"Channel",

	# common
	"Sport",
	"Country",
	"Category",

	# core entities
	"Team",
	"RawTeam",
	"ParsedTeam",
	"PlayerTeamInfo",
	"RawPlayerTeamInfo",
	"ParsedPlayerTeamInfo",
	"Player",
	"RawPlayer",
	"ParsedPlayer",
	"Manager",
	"RawManager",
	"ParsedManager",
	"Referee",
	"RawReferee",
	"ParsedReferee",
	"Venue",
	"RawVenue",
	"ParsedVenue",
	"Stadium",

    # responses
    "TeamResponse",
    "RawTeamResponse",
    "ParsedTeamResponse",
    "UniqueTournamentSeasonsResponse",
    "RawUniqueTournamentSeasonsResponse",
    "ParsedUniqueTournamentSeasonsResponse",
    "EventsResponse",
    "RawEventsResponse",
    "ParsedEventsResponse",
    "RankingsResponse",
    "RawRankingsResponse",
    "ParsedRankingsResponse",
    "ChannelScheduleResponse",
    "RawChannelScheduleResponse",
    "ParsedChannelScheduleResponse",
    "CountryChannelsResponse",
    "LineupsResponse",
    "RawLineupsResponse",
    "ParsedLineupsResponse",
    "EventStatisticsResponse",
    "MomentumGraphResponse",

	# tournament / stage / event
	"Season",
	"RawSeason",
	"ParsedSeason",
	"UniqueTournament",
	"RawUniqueTournament",
	"ParsedUniqueTournament",
	"Tournament",
	"RawTournament",
	"ParsedTournament",
	"UniqueStage",
	"StageType",
	"StageInfo",
	"StageParent",
	"RawStageParent",
	"ParsedStageParent",
	"Stage",
	"RawStage",
	"ParsedStage",
	"Event",
	"RawEvent",
	"ParsedEvent",
	"Round",
	"EventScore",
	"EventTime",
	"EventPeriodLabels",

	# leaderboard
	"TeamStandingsEntry",
	"RawTeamStandingsEntry",
	"ParsedTeamStandingsEntry",
	"TeamStandings",
	"RawTeamStandings",
	"ParsedTeamStandings",
	"RacingStandingsEntry",
	"RawRacingStandingsEntry",
	"ParsedRacingStandingsEntry",
    "RankingType",
    "RawRankingType",
    "ParsedRankingType",
	"RankingEntry",
	"RawRankingEntry",
	"ParsedRankingEntry",

	# search
	"SearchResult",
	"RawSearchResult",
	"ParsedSearchResult",

	# details
	"ParsedManagerCareerHistoryItem",
	"ParsedPlayerPreviousTeam",
	"ParsedPlayerSeasonStats",
	"ParsedTeamPlayers",
	"PlayerSeasonStatsItem",
	"RawManagerCareerHistoryItem",
	"RawPlayerPreviousTeam",
	"RawPlayerSeasonStats",
	"RawTeamPlayers",
	"TeamSeasonStats",
	"TeamYearStats",
	"TeamYearSurfaceStats",
	"VenueStatistics",
	"Incident",
	"MomentumPoint",
	"ParsedLineup",
	"PeriodStatistics",
	"RawLineup",
	"StatisticsGroup",
	"StatisticsItem",
	"Lap",
	"DriverCareerHistory",
	"DriverPerformance",
	"RaceResults",
	"SeasonCareerHistory",
	"TotalCareerHistory",
	"RawDriverCareerHistory",
	"RawDriverPerformance",
	"RawRaceResults",
	"RawSeasonCareerHistory",
	"RawTotalCareerHistory",
]