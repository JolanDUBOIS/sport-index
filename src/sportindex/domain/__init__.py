"""Domain model package for sportindex — defines entities and collections
representing sports data and their relationships (events, competitions, competitors, etc.).

Main elements provided in this package:
- Core entities: `Sport`, `Country`, `Category`.
- Base types: `BaseEntity`, `IdentifiableEntity`, `EntityCollection`.
- Competition models: `Competition`, `Season`.
- Event models: `Event`, `EventCollection`, `Period`, `Lineups`, `Incident`,
  `EventStatistics`, `MomentumGraph`, `MatchCompetitors`, `MatchScore`, `Round`.
- Competitors: `Competitor`, `PlayerInfo`, `Amount`.
- Leaderboards: `Standings`, `Rankings`, `StandingsEntry`, `RankingsEntry`,
  `Promotion`, `Gender`.
- Supporting models: `Manager`, `ManagerCareerHistory`, `Referee`, `Cards`,
  `Venue`, `EventChannels`, `Channel`, `Incident`, etc.
- Utilities: `get_sports`.
"""

import logging
logger = logging.getLogger(__name__)

from .base import BaseEntity, IdentifiableEntity, EntityCollection
from .channel import EventChannels, Channel
from .competition import Competition
from .competitor import Competitor, Team, Player, PlayerInfo
from .core import Sport, Country, Category
from .event import Event, MatchEvent, StageEvent, EventCollection, EventAwareMixin
from .enums import Gender
from .incident import Incident
from .leaderboard import (
    Standings, Rankings,
    StandingsEntry, RankingsEntry,
)
from .manager import Manager
from .referee import Referee
from .season import Season
from .static import get_sports
from .types import EventFormat
from .venue import Venue
