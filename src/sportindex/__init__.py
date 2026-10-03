"""
sport-index: A unified Python SDK for sports data.

Provides the `SportClient` as a clean entry point to access a rich, object-oriented
domain model of sports data (competitions, seasons, events, competitors, etc.).
Designed for intuitive navigation of relational sports data without the hassle of
manual API routing.

Note: This library accesses unofficial APIs and may rely on web scraping.
Use responsibly and comply with the respective providers' terms of service.
"""

import logging
from importlib.metadata import PackageNotFoundError, version

from . import exceptions
from .api_client import (
    Amount,
    EventStatus,
    MatchPeriod,
    MomentumPoint,
    PeriodStats,
    Promotion,
    Round,
    Score,
    StageTier,
    TennisGame,
    TennisGameScore,
    TennisPoint,
    TennisSet,
)
from .client import SportClient

# Import domain types in logical groups (alphabetical within each group)
from .domain import (
    Athlete,
    AthleteInfo,
    BaseEntity,
    Cards,
    Category,
    Channel,
    Competition,
    Competitor,
    Country,
    EntityCollection,
    Event,
    EventAwareMixin,
    EventCollection,
    Gender,
    IdentifiableEntity,
    Incident,
    Manager,
    ManagerTenure,
    MatchCompetitors,
    MatchEvent,
    MatchLineups,
    Rankings,
    RankingsEntry,
    Referee,
    ScoredEntityCollection,
    SearchableMixin,
    Season,
    Sport,
    StageEvent,
    Standings,
    StandingsEntry,
    Team,
    Venue,
)

logging.getLogger(__name__).addHandler(logging.NullHandler())


try:
    __version__ = version("sport-index")
except PackageNotFoundError:
    __version__ = "unknown"


__all__ = [
    # Public API
    "SportClient",

    # Base / collections
    "BaseEntity",
    "IdentifiableEntity",
    "SearchableMixin",

    # Collections
    "EntityCollection",
    "ScoredEntityCollection",
    "EventCollection",

    # Core
    "Category",
    "Country",
    "Gender",
    "Sport",

    # Competitors
    "Competitor",
    "Team",
    "Athlete",
    "AthleteInfo",

    # Competition / seasons
    "Competition",
    "Season",

    # Channels
    "Channel",

    # Events
    "Event",
    "MatchEvent",
    "StageEvent",
    "EventAwareMixin",
    "MatchCompetitors",
    "MatchLineups",

    # Incidents
    "Incident",

    # Leaderboards
    "Rankings",
    "RankingsEntry",
    "Standings",
    "StandingsEntry",

    # People / staff
    "Manager",
    "ManagerTenure",
    "Referee",
    "Cards",

    # Venues
    "Venue",

    # Provider types
    "Amount",
    "EventStatus",
    "MatchPeriod",
    "MomentumPoint",
    "PeriodStats",
    "Promotion",
    "Round",
    "Score",
    "StageTier",
    "TennisGame",
    "TennisGameScore",
    "TennisPoint",
    "TennisSet",

    # Exceptions / submodules
    "exceptions",
]
