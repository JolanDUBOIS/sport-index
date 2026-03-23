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

from .domain import (
    Amount,
    BaseEntity,
    Cards,
    Category,
    Channel,
    Competition,
    Competitor,
    Country,
    EntityCollection,
    Event,
    EventCollection,
    EventChannels,
    EventStatistics,
    Gender,
    IdentifiableEntity,
    Incident,
    Lineups,
    Manager,
    ManagerCareerHistory,
    MatchCompetitors,
    MatchScore,
    MomentumGraph,
    Period,
    PlayerInfo,
    Promotion,
    Rankings,
    Referee,
    Round,
    Season,
    Sport,
    Standings,
    Venue,
)

from .provider import (
    FetchError,
    NotFoundError,
    RateLimitError,
)

__all__ = [
    # Core
    "SportClient",
    
    # Domain Models
    "Amount",
    "BaseEntity",
    "Cards",
    "Category",
    "Channel",
    "Competition",
    "Competitor",
    "Country",
    "EntityCollection",
    "Event",
    "EventCollection",
    "EventChannels",
    "EventStatistics",
    "Gender",
    "IdentifiableEntity",
    "Incident",
    "Lineups",
    "Manager",
    "ManagerCareerHistory",
    "MatchCompetitors",
    "MatchScore",
    "MomentumGraph",
    "Period",
    "PlayerInfo",
    "Promotion",
    "Rankings",
    "Referee",
    "Round",
    "Season",
    "Sport",
    "Standings",
    "Venue",
    
    # Exceptions
    "FetchError",
    "NotFoundError",
    "RateLimitError",
]