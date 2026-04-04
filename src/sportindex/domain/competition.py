from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Optional, Literal, overload

from . import logger
from .base import IdentifiableEntity, EntityCollection
from .types import EventFormat
from .utils import merge_pydantic_models
from sportindex.exceptions import ProviderNotFoundError, FetchError, EntityNotFoundError, DomainError
from sportindex.provider.models import _UniqueTournamentData, _UniqueStageData

if TYPE_CHECKING:
    from .core import Category, Sport
    from .season import Season
    from sportindex.provider import SofascoreProvider


class Competition(IdentifiableEntity):
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
    _data: _UniqueTournamentData | _UniqueStageData
    _REPR_FIELDS = ("id", "name", "slug", "sport", "category")
    _TYPE_MAP = {_UniqueTournamentData: 1, _UniqueStageData: 2}
    _FORMAT_MAP = {_UniqueTournamentData: "match", _UniqueStageData: "stage"}

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

    @property
    def format(self) -> EventFormat:
        """The event format for this competition."""
        try:
            return self._FORMAT_MAP[type(self._data)]
        except KeyError:
            raise TypeError(f"Unsupported competition data type {type(self._data)}.")

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

    def _full_load(self) -> None:
        """
        Lazy-loads the complete competition from the provider.
        Called automatically when accessing properties that require full details
        missing from the initial lightweight API response.
        """
        if self._full_loaded:
            return

        self._data = merge_pydantic_models(self._data, self._fetch_entity(self._data.id, self._provider, type(self._data), strict=False))

        self._full_loaded = True
        self._clear_cache()

    @classmethod
    def from_id(cls, competition_id: int, provider: SofascoreProvider) -> Competition:
        """Fetch a competition by its ID."""
        raw_id, type_idx = cls.decode_id(competition_id)
        type_map_reverse = {v: k for k, v in cls._TYPE_MAP.items()}

        if type_idx not in type_map_reverse:
            raise TypeError(f"Invalid competition ID {competition_id}: unknown type index {type_idx}")

        data_cls = type_map_reverse[type_idx]
        entity_data = cls._fetch_entity(raw_id, provider, data_cls, strict=False)

        return cls(entity_data, provider)

    @classmethod
    def search(cls, query: str, provider: SofascoreProvider, max_results: int = 20) -> EntityCollection[Competition]:
        """Search for competitions matching the given query, returning up to max_results results."""
        entities = []
        for page in range(51): # Sofascore has a maximum of 50 pages of search results
            all_matches = provider.search_all(query=query, page=page)
            if not all_matches:
                break
            for item in all_matches:
                if isinstance(item.entity, (_UniqueTournamentData, _UniqueStageData)):
                    entities.append(Competition(item.entity, provider))
            if len(entities) >= max_results:
                break
        return EntityCollection(entities[:max_results])

    @overload
    @classmethod
    def _fetch_entity(cls, raw_id: int, provider: SofascoreProvider, data_cls: type[_UniqueTournamentData | _UniqueStageData], strict: Literal[True] = True) -> _UniqueTournamentData | _UniqueStageData: ...

    @overload
    @classmethod
    def _fetch_entity(cls, raw_id: int, provider: SofascoreProvider, data_cls: type[_UniqueTournamentData | _UniqueStageData], strict: Literal[False]) -> Optional[_UniqueTournamentData | _UniqueStageData]: ...

    @classmethod
    def _fetch_entity(cls, raw_id: int, provider: SofascoreProvider, data_cls: type[_UniqueTournamentData | _UniqueStageData], strict: bool = True) -> Optional[_UniqueTournamentData | _UniqueStageData]:
        """Fetch the complete competition data from the provider by its raw ID and data class."""
        try:
            if data_cls == _UniqueTournamentData:
                return cls._fetch_ut(raw_id, provider)
            elif data_cls == _UniqueStageData:
                return cls._fetch_us(raw_id, provider)
            else:
                raise TypeError(f"Unsupported data class {data_cls} for competition entity fetch")
        except ProviderNotFoundError:
            logger.debug(f"Competition entity with id {raw_id} and data class {data_cls} not found during fetch")
            if strict:
                raise EntityNotFoundError(f"Competition entity with id {raw_id} not found") from None
        except FetchError as e:
            logger.debug(f"Network error while fetching competition entity with id {raw_id} and data class {data_cls}: {e}")
            if strict:
                raise DomainError(f"Network error while fetching competition entity with id {raw_id}") from e
        return None

    @staticmethod
    def _fetch_ut(raw_id: int, provider: SofascoreProvider) -> _UniqueTournamentData:
        """Fetch a unique tournament by its ID."""
        return provider.get_unique_tournament(raw_id)

    @staticmethod
    def _fetch_us(raw_id: int, provider: SofascoreProvider) -> _UniqueStageData:
        """Fetch a unique stage by its ID."""
        us_seasons = provider.get_unique_stage_seasons(raw_id)
        if not us_seasons:
            raise ProviderNotFoundError(f"Unique stage with id {raw_id} not found")
        return us_seasons[0].unique_stage
