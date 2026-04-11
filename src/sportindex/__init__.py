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
from importlib.metadata import version, PackageNotFoundError

logging.getLogger(__name__).addHandler(logging.NullHandler())

try:
    __version__ = version("sport-index")
except PackageNotFoundError:
    __version__ = "unknown"

from .client import SportClient

# Import domain types in logical groups (alphabetical within each group)
from .domain import (
    # Base
    BaseEntity,
    IdentifiableEntity,
    SearchableMixin,

    # Collections
    EntityCollection,
    ScoredEntityCollection,
    EventCollection,

    # Core
    Category,
    Country,
    Gender,
    Sport,

    # Competitors
    Competitor,
    Team,
    Player,
    PlayerInfo,

    # Competition / seasons
    Competition,
    Season,

    # Channels
    Channel,

    # Events
    Event,
    MatchEvent,
    StageEvent,
    EventFormat,
    EventAwareMixin,
    MatchCompetitors,
    MatchLineups,

    # Incidents
    Incident,

    # Leaderboards
    Rankings,
    RankingsEntry,
    Standings,
    StandingsEntry,

    # People / staff
    Manager,
    ManagerTenure,
    Referee,
    Cards,

    # Venues
    Venue,
)

from .provider import (
    Amount,
    EventStatus,
    MatchPeriod,
    MomentumPoint,
    PeriodStats,
    Promotion,
    Round, 
    Score,
    StageTier
)

from . import exceptions

__all__ = [
    # Public API
    "SportClient",

    # Base / collections
    "BaseEntity",
    "IdentifiableEntity",
    "ScoredItem",
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
    "Player",
    "PlayerInfo",

    # Competition / seasons
    "Competition",
    "Season",

    # Channels
    "Channel",

    # Events
    "Event",
    "MatchEvent",
    "StageEvent",
    "EventFormat",
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

    # Exceptions / submodules
    "exceptions",
]