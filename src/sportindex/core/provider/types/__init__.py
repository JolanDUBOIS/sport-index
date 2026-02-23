"""
TypedDict definitions for Sofascore API responses.

These types document the shape of raw API data returned by the provider.
Keys are in camelCase to match the API's JSON response format.

All types use ``total=False`` — every key is optional — because field presence
varies by endpoint, sport, and nesting context (e.g. a Team inside an Event
has fewer fields than a Team from the /team/{id} endpoint).

Conventions:
  - ASSUMPTION: marks a type choice I'm not 100% sure about
  - REMARK: notes about refactoring, API quirks, or things to revisit
  - "Parsed*" types are output shapes from parsers.py, NOT raw API shapes

Submodules:
  - common:       Core shared types (RawSport, RawCountry, RawCategory)
  - primitives:   Small reusable blocks (RawAmount, RawStatus, RawPerformance, …)
  - tournament:   Tournaments, seasons (RawTournament, RawUniqueTournament, RawSeason)
  - entities:     Teams, players, managers, referees, venues
  - event:        Events, scores, rounds
  - stages:       Stages, races (motorsport, cycling, multi-event sports)
  - leaderboard:  Standings, rankings
  - responses:    API response envelopes (wrappers around entities)
  - details/:     Detailed / nested types (lineups, stats, incidents, …)
"""

from .common import (
    RawCategory,
    RawCountry,
    RawSport,
)
from .primitives import (
    RawAmount,
    RawChannel,
    RawCoordinates,
    RawPerformance,
    RawSearchResult,
    RawStatus,
)
from .tournament import (
    RawSeason,
    RawTournament,
    RawUniqueTournament,
)
from .entities import (
    RawCity,
    RawManager,
    RawPlayer,
    RawPlayerTeamInfo,
    RawReferee,
    RawStadium,
    RawTeam,
    RawVenue,
)
from .event import (
    RawEvent,
    RawEventPeriodLabels,
    RawEventScore,
    RawEventTime,
    RawRound,
)
from .stages import (
    RawStage,
    RawStageInfo,
    RawStageParent,
    RawStageType,
    RawUniqueStage,
)
from .leaderboard import (
    RawPromotion,
    RawRacingStandingsEntry,
    RawRankingEntry,
    RawRankingType,
    RawTeamStandings,
    RawTeamStandingsEntry,
)
from .responses import (
    RawChannelScheduleResponse,
    RawCountryChannelsResponse,
    RawEventStatisticsResponse,
    RawEventsResponse,
    RawLineupsResponse,
    RawMomentumGraphResponse,
    RawRankingsResponse,
    RawTeamResponse,
    RawUniqueTournamentSeasonsResponse,
)
from .details import (
    # details/entities
    RawManagerCareerHistoryItem,
    RawPlayerPreviousTeam,
    RawPlayerSeasonStats,
    RawPlayerSeasonStatsItem,
    RawTeamPlayers,
    RawTeamSeasonStats,
    RawTeamYearStats,
    RawTeamYearSurfaceStats,
    RawVenueStatistics,
    # details/event
    RawIncident,
    RawLineup,
    RawMomentumPoint,
    RawPeriodStatistics,
    RawStatisticsGroup,
    RawStatisticsItem,
    # details/stage
    RawDriverCareerHistory,
    RawDriverPerformance,
    RawLap,
    RawRaceResults,
    RawSeasonCareerHistory,
    RawTotalCareerHistory,
)

__all__ = [
    # common
    "RawCategory",
    "RawCountry",
    "RawSport",
    # primitives
    "RawAmount",
    "RawChannel",
    "RawCoordinates",
    "RawPerformance",
    "RawSearchResult",
    "RawStatus",
    # tournament
    "RawSeason",
    "RawTournament",
    "RawUniqueTournament",
    # entities
    "RawCity",
    "RawManager",
    "RawPlayer",
    "RawPlayerTeamInfo",
    "RawReferee",
    "RawStadium",
    "RawTeam",
    "RawVenue",
    # event
    "RawEvent",
    "RawEventPeriodLabels",
    "RawEventScore",
    "RawEventTime",
    "RawRound",
    # stages
    "RawStage",
    "RawStageInfo",
    "RawStageParent",
    "RawStageType",
    "RawUniqueStage",
    # leaderboard
    "RawPromotion",
    "RawRacingStandingsEntry",
    "RawRankingEntry",
    "RawRankingType",
    "RawTeamStandings",
    "RawTeamStandingsEntry",
    # responses (API endpoint envelopes)
    "RawChannelScheduleResponse",
    "RawCountryChannelsResponse",
    "RawEventStatisticsResponse",
    "RawEventsResponse",
    "RawLineupsResponse",
    "RawMomentumGraphResponse",
    "RawRankingsResponse",
    "RawTeamResponse",
    "RawUniqueTournamentSeasonsResponse",
    # details/entities
    "RawManagerCareerHistoryItem",
    "RawPlayerPreviousTeam",
    "RawPlayerSeasonStats",
    "RawPlayerSeasonStatsItem",
    "RawTeamPlayers",
    "RawTeamSeasonStats",
    "RawTeamYearStats",
    "RawTeamYearSurfaceStats",
    "RawVenueStatistics",
    # details/event
    "RawIncident",
    "RawLineup",
    "RawMomentumPoint",
    "RawPeriodStatistics",
    "RawStatisticsGroup",
    "RawStatisticsItem",
    # details/stage
    "RawDriverCareerHistory",
    "RawDriverPerformance",
    "RawLap",
    "RawRaceResults",
    "RawSeasonCareerHistory",
    "RawTotalCareerHistory",
]
