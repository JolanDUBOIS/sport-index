from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

from .core import BaseModel
from .participants import Manager, Player, Referee, Team
from .tournament import UniqueTournament
from .venue import Venue


SEARCH_TYPE_MAPPING: dict[str, type[BaseModel]] = {
    "manager": Manager,
    "player": Player,
    "referee": Referee,
    "team": Team,
    "uniqueTournament": UniqueTournament,
    "venue": Venue,
}

EntityType = Manager | Player | Referee | Team | UniqueTournament | Venue

@dataclass(frozen=True, kw_only=True)
class SearchResult(BaseModel):
    entity: EntityType
    score: float
    type: Literal["manager", "player", "referee", "team", "uniqueTournament", "venue"]

    @classmethod
    def _from_api(cls, raw: dict) -> SearchResult:
        entity_type = raw.get("type")
        entity_cls = SEARCH_TYPE_MAPPING.get(entity_type)
        if not entity_cls:
            raise ValueError(f"Unsupported search result type: {entity_type}")
        return SearchResult(
            entity=entity_cls.from_api(raw.get("entity")),
            score=raw.get("score"),
            type=entity_type
        )
