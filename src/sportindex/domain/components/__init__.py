import logging
logger = logging.getLogger(__name__)

from .common import (
    Gender,
    Amount,
    Promotion,
    Performance,
)
from .event import (
    MatchCompetitors,
    MatchScore,
    EventRound,
    TeamLineup,
    MatchLineups,
    MatchMomentumPoint,
    MatchPeriod,
    StatEntry,
    StatGroup,
    PeriodStats,
)
from .incidents import (
    IncidentType,
    Incident,
    GoalIncident,
    PenaltyIncident,
    PenaltyShootoutIncident,
    CardIncident,
    PeriodIncident,
    VarDecisionIncident,
    SubstitutionIncident,
    ExtraTimeIncident,
)
from .manager import ManagerTenure
from .referee import Cards

__all__ = [
    # Components (small, composable dataclasses)
    "Amount",
    "Cards",
    "EventRound",
    "Gender",
    "ManagerTenure",
    "MatchCompetitors",
    "MatchLineups",
    "MatchMomentumPoint",
    "MatchPeriod",
    "MatchScore",
    "PeriodStats",
    "Performance",
    "Promotion",
    "StatEntry",
    "StatGroup",
    "TeamLineup",

    # Incidents
    "Incident",
    "IncidentType",
    "GoalIncident",
    "PenaltyIncident",
    "PenaltyShootoutIncident",
    "CardIncident",
    "PeriodIncident",
    "VarDecisionIncident",
    "SubstitutionIncident",
    "ExtraTimeIncident",
]