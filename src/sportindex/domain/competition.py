from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from . import logger
from .base import IdentifiableEntity, EntityCollection
from .utils import merge_pydantic_models
from sportindex.exceptions import InsufficientDataError, ProviderNotFoundError, FetchError, EntityNotFoundError, DomainError
from sportindex.provider.models import _UniqueTournamentData, _UniqueStageData

if TYPE_CHECKING:
    from .core import Category, Sport
    from .season import Season
    from sportindex.provider import SofascoreProvider


class Competition(IdentifiableEntity[_UniqueTournamentData | _UniqueStageData]):
    """A competition, e.g., 'Ligue 1', 'Rolland Garros'.

    Can represent either a unique tournament or a unique stage.
    Provides access to its category, sport, and associated seasons.

    Attributes:
        id (int): Unique ID, encoded from source ID and type.
        name (str): Competition name.
        slug (str): URL-friendly slug.
        sport (Sport): Parent sport.
        category (Category): Parent category (lazy-loaded).
        seasons (EntityCollection[Season]): Seasons of this competition (lazy-loaded).

    Raises:
        TypeError: If data is not UniqueTournament or UniqueStage.
    """
    _REPR_FIELDS = ("id", "name", "slug", "sport", "category")
    _TYPE_MAP = {_UniqueTournamentData: 1, _UniqueStageData: 2}

    def __init__(self, data: _UniqueTournamentData | _UniqueStageData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider)

        if not isinstance(data, (_UniqueTournamentData, _UniqueStageData)):
            raise TypeError(f"Competition data must be either _UniqueTournamentData or _UniqueStageData, got {type(data)}")

        self._full_loaded = False

    @property
    def id(self) -> int:
        """The unique ID of the competition."""
        type_idx = self._TYPE_MAP[type(self._data)]
        return self.encode_id(self._data.id, type_idx)

    @property
    def name(self) -> str:
        """The name of the competition."""
        return self._data.name

    @property
    def slug(self) -> str:
        """The slug of the competition."""
        return self._data.slug

    @property
    def sport(self) -> Sport:
        """The sport this competition belongs to."""
        return self.category.sport

    @cached_property
    def category(self) -> Category:
        """The category this competition belongs to."""
        from .core import Category
        return Category(self._data.category, self._provider)

    @cached_property
    def seasons(self) -> EntityCollection[Season]:
        """Fetch all seasons for this competition."""
        from .season import Season
        if isinstance(self._data, _UniqueTournamentData):
            return EntityCollection([
                Season(s, self._provider, competition=self)
                for s in self._provider.get_unique_tournament_seasons(self._data.id)
            ])
        elif isinstance(self._data, _UniqueStageData):
            return EntityCollection([
                Season(s, self._provider, competition=self)
                for s in self._provider.get_unique_stage_seasons(self._data.id)
            ])
        else:
            raise TypeError(f"Competition data must be either _UniqueTournamentData or _UniqueStageData, got {type(self._data)}")

    def _full_load(self) -> None:
        """
        Lazy-loads the complete competition from the provider.
        Called automatically when accessing properties that require full details
        missing from the initial lightweight API response.
        """
        if self._full_loaded:
            return
        try:
            if isinstance(self._data, _UniqueTournamentData):
                self._data = merge_pydantic_models(self._data, self._provider.get_unique_tournament(self._data.id))
            elif isinstance(self._data, _UniqueStageData):
                logger.debug(f"No endpoint available to fully load unique stage yet, skipping full load...")
            if not isinstance(self._data, (_UniqueTournamentData, _UniqueStageData)):
                raise TypeError(f"Competition data must be either _UniqueTournamentData or _UniqueStageData after full load, got {type(self._data)}")
            self._full_loaded = True
        except ProviderNotFoundError:
            logger.debug(f"Competition with id {self._data.id} not found during full load")
            self._full_loaded = True
        except FetchError as e:
            logger.debug(f"Network error while fully loading competition with id {self._data.id}: {e}")
            self._full_loaded = True
        self._clear_cache()

    @classmethod
    def from_id(cls, competition_id: int, provider: SofascoreProvider) -> Competition:
        """Fetch a competition by its ID."""
        raw_id, type_idx = cls.decode_id(competition_id)
        type_map_reverse = {v: k for k, v in cls._TYPE_MAP.items()}
        # exceptions imported at module level

        if type_idx not in type_map_reverse:
            raise TypeError(f"Invalid competition ID {competition_id}: unknown type index {type_idx}")

        data_cls = type_map_reverse[type_idx]
        try:
            if data_cls == _UniqueTournamentData:
                parsed_data = provider.get_unique_tournament(raw_id)
            elif data_cls == _UniqueStageData:
                us_seasons = provider.get_unique_stage_seasons(raw_id)
                if us_seasons:
                    parsed_data = us_seasons[0].unique_stage
                else:
                    raise InsufficientDataError(f"Could not find any seasons for unique stage with ID {raw_id}, cannot construct competition")
            else:
                raise TypeError(f"Unsupported data class {data_cls} for competition ID {competition_id}")
        except ProviderNotFoundError as e:
            raise EntityNotFoundError(f"Competition with id {competition_id} not found") from e
        except FetchError as e:
            raise DomainError(f"Network error while fetching competition {competition_id}") from e

        return cls(parsed_data, provider)

    @classmethod
    def search(cls, query: str, provider: SofascoreProvider) -> EntityCollection[Competition]:
        """Search for competitions matching the given query (up to the first 20 matches)."""
        entities = []
        for page in range(51): # Sofascore has a maximum of 50 pages of search results
            all_matches = provider.search_all(query=query, page=page)
            if not all_matches:
                break
            for item in all_matches:
                if isinstance(item.entity, (_UniqueTournamentData, _UniqueStageData)):
                    entities.append(Competition(item.entity, provider))
            if len(all_matches) > 20:
                break
        return EntityCollection(entities[:20])
