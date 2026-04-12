"""Domain model package for sportindex — defines entities and collections
representing sports data and their relationships (events, competitions, competitors, etc.).

Main elements provided in this package:
- Core entities: `Sport`, `Country`, `Category`.
- Base types: `BaseEntity`, `IdentifiableEntity`, `EntityCollection`.
- Competition models: `Competition`, `Season`.
- Event models: `Event`, `EventCollection`, `Period`, `Lineups`, `Incident`,
  `EventStatistics`, `MomentumGraph`, `MatchCompetitors`, `MatchScore`, `Round`.
- Competitors: `Competitor`, `AthleteInfo`, `Amount`.
- Leaderboards: `Standings`, `Rankings`, `StandingsEntry`, `RankingsEntry`,
  `Promotion`, `Gender`.
- Supporting models: `Manager`, `ManagerCareerHistory`, `Referee`, `Cards`,
  `Venue`, `Channel`, `Incident`, etc.
"""

import logging
logger = logging.getLogger(__name__)

from .base import BaseEntity, IdentifiableEntity, SearchableMixin
from .channel import Channel
from .collections import EntityCollection, ScoredEntityCollection, EventCollection
from .competition import Competition
from .competitor import Competitor, Team, Athlete, AthleteInfo
from .core import Sport, Country, Category
from .event import Event, MatchEvent, StageEvent, EventAwareMixin, MatchCompetitors, MatchLineups
from .enums import Gender
from .incident import Incident
from .leaderboard import Standings, Rankings, StandingsEntry, RankingsEntry
from .manager import Manager, ManagerTenure
from .referee import Referee, Cards
from .season import Season
from .types import SportContestNature
from .venue import Venue
