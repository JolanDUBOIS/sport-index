"""
Detailed / nested dataclass types for entities, events, and stages.

Re-exports every public type from the three submodules so that the parent
``types`` package can do ``from .details import …``.
"""

from .entities import (
    RawManagerCareerHistoryItem,
    RawPlayerPreviousTeam,
    RawPlayerSeasonStats,
    RawPlayerSeasonStatsItem,
    RawTeamPlayers,
    RawTeamSeasonStats,
    RawTeamYearStats,
    RawTeamYearSurfaceStats,
    RawVenueStatistics,
)
from .event import (
    RawIncident,
    RawLineup,
    RawMomentumPoint,
    RawPeriodStatistics,
    RawStatisticsGroup,
    RawStatisticsItem,
)
from .stage import (
    RawDriverCareerHistory,
    RawDriverPerformance,
    RawLap,
    RawRaceResults,
    RawSeasonCareerHistory,
    RawTotalCareerHistory,
)

__all__ = [
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