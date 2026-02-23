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
  - common:       Core primitives (RawSport, RawCountry, RawStatus, etc.)
  - entities:     Tournaments, teams, players, managers, referees, venues
  - events:       Events, lineups, statistics, incidents, parsed output types
  - stages:       Stages, races (motorsport, cycling, multi-event sports)
  - leaderboards: Standings, rankings, channels, search, transfers
"""

# TODO - Check if not missing imports...

from .common import (
    RawCategory,
    RawCountry,
    RawSport,
)
from .stages import (
    RawDriverPerformance,
    RawLap,
    RawRace,
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
    RawRankingsResponse,
    RawRankingType,
    RawTeamStandings,
    RawTeamStandingsEntry,
)
from .entities import (
    RawManager,
    RawPerformance,
    RawPlayer,
    RawPlayerPreviousTeam,
    RawPlayerTeamInfo,
    RawReferee,
    RawSeason,
    RawStadium,
    RawTeam,
    RawTeamPlayers,
    RawTeamSeasonStats,
    RawTournament,
    RawUniqueTournament,
    RawUniqueTournamentSeasons,
    RawVenue,
)
from .event import (
    RawEvent,
    RawEventPeriodLabels,
    RawEventsResponse,
    RawEventScore,
    RawEventStatisticsResponse,
    RawEventTime,
    RawIncident,
    RawLineup,
    RawLineupsResponse,
    RawMomentumGraphResponse,
    RawMomentumPoint,
    RawPeriodStatistics,
    RawRound,
    RawStatisticsGroup,
    RawStatisticsItem,
)
from .primitives import (
    RawAmount,
    RawCoordinates,
    RawChannel,
    RawChannelSchedule,
    RawCountryChannelsResponse,
    RawSearchResult,
)

__all__ = [
    # common
    "RawAmount",
    "RawCategory",
    "RawCoordinates",
    "RawCountry",
    "RawSport",
    "RawStadium",
    "RawStatus",
    "RawTransferWindow",
    # entities
    "RawManager",
    "RawPerformance",
    "RawPlayer",
    "RawPlayerPreviousTeam",
    "RawPlayerTeamInfo",
    "RawReferee",
    "RawSeason",
    "RawTeam",
    "RawTeamPlayers",
    "RawTeamSeasonStats",
    "RawTournament",
    "RawUniqueTournament",
    "RawUniqueTournamentSeasons",
    "RawVenue",
    # events
    "RawEvent",
    "RawEventPeriodLabels",
    "RawEventsResponse",
    "RawEventScore",
    "RawEventStatisticsResponse",
    "RawEventTime",
    "RawIncident",
    "RawLineup",
    "RawLineupsResponse",
    "RawMomentumGraphResponse",
    "RawMomentumPoint",
    "RawPeriodStatistics",
    "RawRound",
    "RawStatisticsGroup",
    "RawStatisticsItem",
    # stages
    "RawDriverPerformance",
    "RawLap",
    "RawRace",
    "RawStage",
    "RawStageInfo",
    "RawStageParent",
    "RawStageType",
    "RawUniqueStage",
    # leaderboards, channels, search, transfers
    "RawChannel",
    "RawChannelSchedule",
    "RawCountryChannelsResponse",
    "RawPromotion",
    "RawRacingStandingsEntry",
    "RawRankingEntry",
    "RawRankingsResponse",
    "RawRankingType",
    "RawSearchResult",
    "RawStage",
    "RawStageInfo",
    "RawStageParent",
    "RawStageType",
    "RawTeamStandings",
    "RawTeamStandingsEntry",
    "RawTransfer",
    "RawUniqueStage",
]
