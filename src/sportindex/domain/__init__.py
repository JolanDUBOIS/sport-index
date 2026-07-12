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

from .base import BaseEntity, IdentifiableEntity, SearchableMixin
from .channel import Channel
from .collections import EntityCollection, EventCollection, ScoredEntityCollection
from .competition import Competition
from .competitor import Athlete, AthleteInfo, Competitor, Team
from .core import Category, Country, Sport
from .enums import Gender
from .event import (
    Event,
    EventAwareMixin,
    MatchCompetitors,
    MatchEvent,
    MatchLineups,
    StageEvent,
)
from .incident import Incident
from .leaderboard import Rankings, RankingsEntry, Standings, StandingsEntry
from .manager import Manager, ManagerTenure
from .referee import Cards, Referee
from .season import Season
from .venue import Venue

__all__ = [
    "BaseEntity",
    "IdentifiableEntity",
    "SearchableMixin",
    "Channel",
    "EntityCollection",
    "EventCollection",
    "ScoredEntityCollection",
    "Competition",
    "Athlete",
    "AthleteInfo",
    "Competitor",
    "Team",
    "Category",
    "Country",
    "Sport",
    "Gender",
    "Event",
    "EventAwareMixin",
    "MatchCompetitors",
    "MatchEvent",
    "MatchLineups",
    "StageEvent",
    "Incident",
    "Rankings",
    "RankingsEntry",
    "Standings",
    "StandingsEntry",
    "Manager",
    "ManagerTenure",
    "Cards",
    "Referee",
    "Season",
    "Venue",
]
