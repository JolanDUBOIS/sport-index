"""
sport-index domain layer.

Domain entities are the public-facing objects of the library.
They wrap raw API data (from ``core.provider``) into Python objects
with lazy-loaded relationships, clean attribute access, and no dicts
leaking to the consumer.

Quick start::

    from sportindex.core.domain import Index

    idx = Index()
    football = idx.sport("football")

    # Navigate the graph
    categories = football.categories           # API call (lazy)
    england = [c for c in categories if c.slug == "england"][0]
    competitions = england.competitions        # API call (lazy)
    pl = [c for c in competitions if "Premier" in c.name][0]
    seasons = pl.seasons                       # API call (lazy)
    latest = seasons[0]
    standings = latest.standings               # API call (lazy)

    for row in standings[0].entries:
        print(f"#{row.position} {row.competitor.name} — {row.points} pts")
"""

import logging

logger = logging.getLogger(__name__)

# Base
from .base import BaseEntity

# Value objects
from .values import (
    Amount,
    Cards,
    Coordinates,
    Performance,
    Promotion,
    Round,
    Score,
    Status,
)

# Core entities
from .core import Sport, Country, Category
from .index import Index
from .competition import Competition, CompetitionDetails
from .season import Season
from .event import (
    Event,
    EventLineups,
    Lineup,
    MatchData,
    MatchDetails,
    MatchResults,
    Momentum,
    MomentumPoint,
    PeriodStatistics,
    RaceData,
    RaceResults,
    StageDetails,
    StatisticsGroup,
    StatisticsItem,
)
from .participant import (
    Competitor,
    Manager,
    Referee,
    TeamDetails,
    PlayerDetails,
)
from .venue import Venue
from .leaderboard import (
    Standings,
    StandingsEntry,
    Rankings,
    RankingsEntry,
)

__all__ = [
    # Base
    "BaseEntity",
    "Index",
    # Values
    "Amount",
    "Cards",
    "Coordinates",
    "Performance",
    "Promotion",
    "Round",
    "Score",
    "Status",
    # Entities
    "Sport",
    "Country",
    "Category",
    "Competition",
    "CompetitionDetails",
    "Season",
    "Event",
    "EventLineups",
    "Lineup",
    "MatchData",
    "MatchDetails",
    "MatchResults",
    "Momentum",
    "MomentumPoint",
    "PeriodStatistics",
    "RaceData",
    "RaceResults",
    "StageDetails",
    "StatisticsGroup",
    "StatisticsItem",
    "Competitor",
    "Manager",
    "Referee",
    "TeamDetails",
    "PlayerDetails",
    "Venue",
    "Standings",
    "StandingsEntry",
    "Rankings",
    "RankingsEntry",
]