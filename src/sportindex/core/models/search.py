from typing import Any

from . import logger
from .base import BaseModel, RawModel, ParsedModel
from .manager import RawManager, ParsedManager
from .player import RawPlayer, ParsedPlayer
from .referee import RawReferee, ParsedReferee
from .team import RawTeam, ParsedTeam
from .tournament import RawUniqueTournament, ParsedUniqueTournament
from .venue import RawVenue, ParsedVenue


ENTITY_MODELS: dict[str, dict[str, type[BaseModel]]] = {
    "team": {
        "raw": RawTeam,
        "parsed": ParsedTeam,
    },
    "player": {
        "raw": RawPlayer,
        "parsed": ParsedPlayer,
    },
    "manager": {
        "raw": RawManager,
        "parsed": ParsedManager,
    },
    "referee": {
        "raw": RawReferee,
        "parsed": ParsedReferee,
    },
    "uniqueTournament": {
        "raw": RawUniqueTournament,
        "parsed": ParsedUniqueTournament,
    },
    "venue": {
        "raw": RawVenue,
        "parsed": ParsedVenue,
    },
}

class SearchResult(BaseModel):
    type: str                 # The entity type
    score: float              # Search relevance score

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._convert_entity()

    def _model_kind(self) -> str | None:
        if isinstance(self, RawModel):
            return "raw"
        if isinstance(self, ParsedModel):
            return "parsed"
        return None

    def _convert_entity(self) -> None:
        if not isinstance(getattr(self, "entity", None), dict):
            return

        kind = self._model_kind()
        if kind is None:
            return

        model_map = ENTITY_MODELS.get(self.type)
        if not model_map:
            return

        target_class = model_map.get(kind)
        if not target_class:
            return

        try:
            self.entity = target_class.from_dict(self.entity)
        except Exception as e:
            logger.warning(
                "Failed to parse search result entity of type '%s': %s",
                self.type,
                e,
            )

class RawSearchResult(SearchResult, RawModel):
    entity: dict[str, BaseModel]    # Shape depends on `type`

class ParsedSearchResult(SearchResult, ParsedModel):
    entity: dict[str, BaseModel]    # Shape depends on `type`
