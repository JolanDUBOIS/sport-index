"""
Detailed / nested dataclass types for entities, events, and stages.

Re-exports every public type from the three submodules so that the parent
``types`` package can do ``from .details import …``.
"""

from .entities import (
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
)
from .event import (
    Incident,
    MomentumPoint,
    ParsedLineup,
    PeriodStatistics,
    RawLineup,
    StatisticsGroup,
    StatisticsItem,
)
from .stage import (
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