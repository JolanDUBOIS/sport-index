"""Domain model package for sportindex — defines entities and collections
representing sports data and their relationships (events, competitions, competitors, etc.).

Main elements provided in this package:
- Core entities: `Sport`, `Country`, `Category`, `Gender`.
- Base types: `BaseEntity`, `IdentifiableEntity`, `EntityCollection`.
- Competition models: `Competition`, `Season`.
- Event models: `Event`, `EventCollection`, `Period`, `Lineups`, `Incident`,
  `EventStatistics`, `MomentumGraph`, `MatchCompetitors`, `MatchScore`, `Round`.
- Competitors: `Competitor`, `PlayerInfo`, `Amount`.
- Leaderboards: `Standings`, `Rankings`, `StandingsEntry`, `RankingsEntry`,
  `Promotion`.
- Supporting models: `Manager`, `ManagerCareerHistory`, `Referee`, `Cards`,
  `Venue`, `EventChannels`, `Channel`.
- Utilities: `get_sports`.
"""

import logging
logger = logging.getLogger(__name__)

from .base import BaseEntity, IdentifiableEntity, EntityCollection
from .channel import EventChannels, Channel
from .competition import Competition, Season
from .competitor import Competitor, PlayerInfo, Amount
from .core import Sport, Country, Category, Gender
from .event import (
    Event, EventCollection,
    Period, Lineups, Incident, EventStatistics, MomentumGraph,
    MatchCompetitors, MatchScore, Round
)
from .leaderboard import (
    Standings, Rankings,
    StandingsEntry, RankingsEntry,
    Promotion
)
from .manager import Manager, ManagerCareerHistory
from .referee import Referee, Cards
from .static import get_sports
from .venue import Venue
