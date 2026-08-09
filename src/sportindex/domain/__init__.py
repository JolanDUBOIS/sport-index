"""Domain model package for sportindex — the entities and collections that make up the
SDK's public surface, and the relationships between them.

Exported from this package:

- Base types: `BaseEntity`, `IdentifiableEntity`, `SearchableMixin`, `EventAwareMixin`.
- Collections: `EntityCollection`, `ScoredEntityCollection`, `EventCollection`.
- Core entities: `Sport`, `Country`, `Category`.
- Competitions and their editions: `Competition`, `Season`.
- Events: `Event` and its two public kinds `MatchEvent` and `StageEvent`, plus the
  `MatchCompetitors` and `MatchLineups` components and the `Incident` union.
- Competitors: `Competitor`, and the richer `Team` and `Athlete` it resolves to, with
  `AthleteInfo`.
- Leaderboards: `Standings` and `StandingsEntry` for a season's tables, `Rankings` and
  `RankingsEntry` for a sport's standing order.
- Supporting entities: `Manager` with `ManagerTenure`, `Referee` with `Cards`, `Venue`,
  `Channel`.
- Enums: `Gender`.

Entities are addressed by SDK ID — see `IdentifiableEntity` — and are normally reached
through `sportindex.SportClient` rather than constructed directly.
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
