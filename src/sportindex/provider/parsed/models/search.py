from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar, Generic

from .base import BaseParsedModel
from .manager import ParsedManager
from .player import ParsedPlayer
from .referee import ParsedReferee
from .stage import ParsedUniqueStage, ParsedStage
from .team import ParsedTeam
from .tournament import ParsedUniqueTournament
from .venue import ParsedVenue
if TYPE_CHECKING:
    from sportindex.provider.raw.models import SearchResult


AnyParsedEntity = (
    ParsedManager
    | ParsedPlayer
    | ParsedReferee
    | ParsedTeam
    | ParsedUniqueTournament
    | ParsedUniqueStage
    | ParsedStage
    | ParsedVenue
)

T = TypeVar("T", bound=AnyParsedEntity)

ENTITY_MODELS: dict[str, type[BaseParsedModel]] = {
    "manager": ParsedManager,
    "player": ParsedPlayer,
    "referee": ParsedReferee,
    "team": ParsedTeam,
    "uniqueTournament": ParsedUniqueTournament,
    "uniqueStage": ParsedUniqueStage,
    "stage": ParsedStage,
    "venue": ParsedVenue,
}

@dataclass
class ParsedSearchResult(BaseParsedModel, Generic[T]):
    type: str                 # The entity type
    score: float              # Search relevance score
    entity: T                 # The parsed entity (e.g. ParsedPlayer, ParsedTeam, etc.)

    @classmethod
    def _parse(cls, raw: SearchResult) -> ParsedSearchResult[AnyParsedEntity]:
        entity_type = raw.get("type")
        entity_cls = ENTITY_MODELS.get(entity_type)
        if not entity_cls:
            raise ValueError(f"Unknown entity type in search result: {entity_type}")
        return cls(
            type=entity_type,
            score=raw.get("score"),
            entity=entity_cls.from_raw(raw.get("entity", {})),
        )
