from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING, Generic, Literal, Self, overload

from typing_extensions import TypeVar

from sportindex.exceptions import (
    DomainError,
    EntityNotFoundError,
    FetchError,
    ProviderNotFoundError,
)
from sportindex.provider.models import _UniqueStageData, _UniqueTournamentData

from .base import SearchableMixin
from .collections import EntityCollection, ScoredEntityCollection
from .types import SportContestNature
from .utils import merge_pydantic_models

if TYPE_CHECKING:
    from sportindex.provider import SofascoreProvider
    from sportindex.provider.models import BaseSchema

    from .core import Category, Sport
    from .event import Event, MatchEvent, StageEvent
    from .season import Season

logger = logging.getLogger(__name__)


E = TypeVar("E", bound="Event", default="Event")

class Competition(SearchableMixin, Generic[E]):
    """A competition, e.g., 'Ligue 1', 'Rolland Garros'.

    Can represent either a unique tournament or a unique stage.
    Provides access to its category, sport, and associated seasons.

    Attributes:
        id (int): Unique ID, encoded from source ID and type.
        name (str): Competition name.
        slug (str): URL-friendly slug.
        sport (Sport): Parent sport.
        event_format (EventFormat): The event format for this competition, either "match" or "stage".
        category (Category): Parent category (lazy-loaded).
        seasons (EntityCollection[Season[E]]): Seasons of this competition (lazy-loaded).

    Methods:
        from_id(competition_id, provider) -> Competition: Fetch a competition by its ID.
        search(query, provider) -> ScoredEntityCollection: Search for competitions matching a query string

    Raises:
        TypeError: If data is not UniqueTournament or UniqueStage.
    """
    _data: _UniqueTournamentData | _UniqueStageData
    _REPR_FIELDS = ("id", "name", "slug", "sport", "category")
    _N_TYPES: int = 2
    _TYPE_MAP: dict[type[BaseSchema], int] = {_UniqueTournamentData: 1, _UniqueStageData: 2}
    _REVERSE_TYPE_MAP: dict[int, type[BaseSchema]] = {1: _UniqueTournamentData, 2: _UniqueStageData}

    @overload
    def __new__(cls, data: _UniqueTournamentData, provider: SofascoreProvider, **kwargs) -> Competition[MatchEvent]: ...

    @overload
    def __new__(cls, data: _UniqueStageData, provider: SofascoreProvider, **kwargs) -> Competition[StageEvent]: ...

    def __new__(cls, data: _UniqueTournamentData | _UniqueStageData, provider: SofascoreProvider, **kwargs):
        return super().__new__(cls)

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
    def sport(self) -> Sport[E]:
        """The sport this competition belongs to."""
        return self.category.sport

    @property
    def sport_nature(self) -> SportContestNature:
        """The nature of the sport for this competition."""
        if isinstance(self._data, _UniqueTournamentData):
            return SportContestNature.OPPOSITION
        if isinstance(self._data, _UniqueStageData):
            return SportContestNature.COMPARISON
        raise TypeError(f"Unsupported competition data type {type(self._data)}.")

    @cached_property
    def category(self) -> Category[E]:
        """The category this competition belongs to."""
        from .core import Category
        return Category(self._data.category, self._provider)

    @cached_property
    def seasons(self) -> EntityCollection[Season[E]]:
        """Fetch all seasons for this competition."""
        from .season import Season
        if isinstance(self._data, _UniqueTournamentData):
            return EntityCollection([
                Season(s, self._provider, competition=self)
                for s in self._provider.get_unique_tournament_seasons(self._data.id)
            ])
        if isinstance(self._data, _UniqueStageData):
            return EntityCollection([
                Season(s, self._provider, competition=self)
                for s in self._provider.get_unique_stage_seasons(self._data.id)
            ])
        raise TypeError(
            f"Internal state error: Expected _data to be _UniqueTournamentData or "
            f"_UniqueStageData, but got {type(self._data).__name__}."
        )

    def _full_load(self) -> None:
        """
        Lazy-loads the complete competition from the provider.
        Called automatically when accessing properties that require full details
        missing from the initial lightweight API response.
        """
        if self._full_loaded:
            return

        self._data = merge_pydantic_models(self._data, self._fetch_entity(self.id, self._provider, strict=False))

        self._full_loaded = True
        self._clear_cache()

    @classmethod
    def from_id(cls, competition_id: int, provider: SofascoreProvider) -> Self:
        """Fetch a competition by its domain ID."""
        if not isinstance(competition_id, int):
            raise TypeError(f"Competition ID must be an integer, got {type(competition_id)}")

        try:
            entity_data = cls._fetch_entity(competition_id, provider)
            instance = cls(entity_data, provider)
            if not issubclass(type(instance), cls):
                raise TypeError(
                    f"ID {competition_id} belongs to a {type(instance).__name__}, but was initialized as a {cls.__name__}. "
                    f"Use {type(instance).__name__}.from_id() instead."
                )
            return instance
        except ProviderNotFoundError as e:
            raise EntityNotFoundError(f"Competition with ID {competition_id} not found") from e
        except FetchError as e:
            raise DomainError(f"Network error while fetching competition with ID {competition_id}") from e

    @classmethod
    def search(cls, query: str, provider: SofascoreProvider, max_results: int = 20) -> ScoredEntityCollection[Competition]:
        """Search for competitions matching the given query, returning up to max_results results."""
        cls._validate_query(query)
        return cls._paginate_search(
            query=query,
            provider=provider,
            search_func=provider.search_all,
            valid_types=(_UniqueTournamentData, _UniqueStageData),
            max_results=max_results
        )

    @overload
    @classmethod
    def _fetch_entity(cls, competition_id: int, provider: SofascoreProvider, strict: Literal[True] = True) -> _UniqueTournamentData | _UniqueStageData: ...

    @overload
    @classmethod
    def _fetch_entity(cls, competition_id: int, provider: SofascoreProvider, strict: Literal[False]) -> _UniqueTournamentData | _UniqueStageData | None: ...

    @classmethod
    def _fetch_entity(cls, competition_id: int, provider: SofascoreProvider, strict: bool = True) -> _UniqueTournamentData | _UniqueStageData | None:
        """Fetch the complete competition data from the provider by its ID."""
        raw_id, type_idx = cls.decode_id(competition_id)

        try:
            if type_idx == 1:
                return cls._fetch_unique_tournament(raw_id, provider)
            if type_idx == 2:
                return cls._fetch_unique_stage(raw_id, provider)
            raise TypeError(f"Invalid competition ID {competition_id}: unknown type index {type_idx}")

        except ProviderNotFoundError:
            logger.debug(f"Competition with ID {competition_id} not found during fetch")
            if strict:
                raise EntityNotFoundError(f"Competition with ID {competition_id} not found during fetch") from None

        except FetchError as e:
            logger.debug(f"Network error while fetching competition with ID {competition_id}: {e}")
            if strict:
                raise DomainError(f"Network error while fetching competition with ID {competition_id}") from e

        return None

    @staticmethod
    def _fetch_unique_tournament(unique_tournament_id: int, provider: SofascoreProvider) -> _UniqueTournamentData:
        """Fetch _UniqueTournamentData by its ID."""
        return provider.get_unique_tournament(unique_tournament_id)

    @staticmethod
    def _fetch_unique_stage(unique_stage_id: int, provider: SofascoreProvider) -> _UniqueStageData:
        """Fetch _UniqueStageData by its ID."""
        us_seasons = provider.get_unique_stage_seasons(unique_stage_id)
        if not us_seasons:
            raise ProviderNotFoundError(f"Unique stage with id {unique_stage_id} not found")
        return us_seasons[0].unique_stage
