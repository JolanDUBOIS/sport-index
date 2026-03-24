from __future__ import annotations

from typing import TypedDict, TypeVar, Generic, TYPE_CHECKING

if TYPE_CHECKING:
    from .manager import RawManager
    from .player import RawPlayer
    from .referee import RawReferee
    from .team import RawTeam
    from .tournament import RawUniqueTournament
    from .venue import RawVenue


T = TypeVar(
    "T",
    "RawTeam",
    "RawPlayer",
    "RawManager",
    "RawReferee",
    "RawUniqueTournament",
    "RawVenue",
)

class RawSearchResult(TypedDict, Generic[T], total=False):
    type: str                 # The entity type (e.g., "team", "player")
    score: float              # Search relevance score
    entity: T
