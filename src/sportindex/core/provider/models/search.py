from __future__ import annotations

from typing import TypedDict, TypeVar, Generic, TYPE_CHECKING

if TYPE_CHECKING:
    from .manager import Manager
    from .player import Player
    from .referee import Referee
    from .team import Team
    from .tournament import UniqueTournament
    from .venue import Venue


T = TypeVar(
    "T",
    "Team",
    "Player",
    "Manager",
    "Referee",
    "UniqueTournament",
    "Venue",
)

class SearchResult(TypedDict, Generic[T], total=False):
    type: str                 # The entity type (e.g., "team", "player")
    score: float              # Search relevance score
    entity: T
