from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .manager import ParsedManager
    from .player import ParsedPlayer
    from .referee import ParsedReferee
    from .team import ParsedTeam
    from .tournament import ParsedUniqueTournament
    from .venue import ParsedVenue
    from sportindex.core.provider.models import SearchResult


ENTITY_MODELS: dict[str, object] = {
    "manager": ParsedManager,
    "player": ParsedPlayer,
    "referee": ParsedReferee,
    "team": ParsedTeam,
    "uniqueTournament": ParsedUniqueTournament,
    "venue": ParsedVenue,
}

@dataclass
class ParsedSearchResult:
    type: str                 # The entity type
    score: float              # Search relevance score
    entity: ParsedPlayer | ParsedReferee | ParsedTeam | ParsedUniqueTournament | ParsedVenue

    @classmethod
    def from_raw(cls, raw: SearchResult) -> ParsedSearchResult:
        entity_type = raw.get("type")
        return cls(
            type=entity_type,
            score=raw.get("score"),
            entity=ENTITY_MODELS.get(entity_type, lambda x: x).from_raw(raw.get("entity", {})),
        )
