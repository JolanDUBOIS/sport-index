from typing import Any

from . import logger
from .base import RawModel
from .entities import RawTeam, RawPlayer, RawManager, RawReferee, RawUniqueTournament, RawVenue


ENTITY_MODELS: dict[str, type[RawModel]] = {
    "team": RawTeam,
    "player": RawPlayer,
    "manager": RawManager,
    "referee": RawReferee,
    "uniqueTournament": RawUniqueTournament,
    "venue": RawVenue,
}

class RawSearchResult(RawModel):
    """A single search result.
    The ``entity`` is a raw dict whose shape depends on ``type``:
        - "team"             → RawTeam
        - "player"           → RawPlayer
        - "manager"          → RawManager
        - "referee"          → RawReferee
        - "uniqueTournament" → RawUniqueTournament
        - "venue"            → RawVenue
    """
    type: str                 # The entity type
    entity: dict[str, Any]    # Shape depends on `type`
    score: float              # Search relevance score

    def __init__(self, **data: Any):
        super().__init__(**data)

        if self.type in ENTITY_MODELS and isinstance(self.entity, dict):
            target_class = ENTITY_MODELS[self.type]
            try:
                self.entity = target_class.from_dict(self.entity)
            except Exception as e:
                logger.warning(
                    "Failed to parse search result entity of type '%s': %s",
                    self.type,
                    e,
                )
