"""
sport-index: Unified Python clients for sports data.

Provides a Client class to access various sports data through a consistent interface.
Supports multiple sports and data types, with models for structured access to results, standings, and more.

Note: This library accesses unofficial APIs and may rely on scraping.
Use responsibly and comply with provider terms of service.
"""

import logging
from importlib.metadata import version, PackageNotFoundError

logging.getLogger(__name__).addHandler(logging.NullHandler())

try:
    __version__ = version("sport-index")
except PackageNotFoundError:
    __version__ = "unknown"

from .core import Client
from .core.models import (
    Category,
    Event,
    Incident,
    Lineup,
    Manager,
    Player,
    Referee,
    RacingStandings,
    Rankings,
    RoundStage,
    Season,
    SeasonStage,
    Team,
    TeamStandings,
    UniqueTournament,
    Venue
)

__all__ = [
    "__version__",
    "Client",
    # Public models
    "Category",
    "Event",
    "Incident",
    "Lineup",
    "Manager",
    "Player",
    "Referee",
    "RacingStandings",
    "Rankings",
    "RoundStage",
    "Season",
    "SeasonStage",
    "Team",
    "TeamStandings",
    "UniqueTournament",
    "Venue",
]
