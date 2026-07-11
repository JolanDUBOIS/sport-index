from __future__ import annotations

import logging
from abc import abstractmethod
from functools import cached_property
from typing import TYPE_CHECKING, overload

from sportindex.api_client.models import _UniqueStageData, _UniqueTournamentData
from sportindex.exceptions import (
    DomainError,
    EntityNotFoundError,
    FetchError,
    ProviderNotFoundError,
)

from .base import SearchableMixin
from .collections import EntityCollection, ScoredEntityCollection

if TYPE_CHECKING:
    from sportindex.api_client import SofascoreProvider

    from .core import Category, Sport
    from .season import Season

logger = logging.getLogger(__name__)


class Competition(SearchableMixin):
    """A competition, e.g., 'Ligue 1', 'Rolland Garros'.

    Can represent either a unique tournament or a unique stage.
    Provides access to its category, sport, and associated seasons.

    Attributes:
        id (str): Unique ID, encoded from source ID and type.
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

    @overload
    def __new__(cls, data: _UniqueTournamentData, provider: SofascoreProvider, **kwargs) -> _TournamentCompetition: ...

    @overload
    def __new__(cls, data: _UniqueStageData, provider: SofascoreProvider, **kwargs) -> _StageCompetition: ...

    def __new__(cls, data: _UniqueTournamentData | _UniqueStageData, provider: SofascoreProvider, **kwargs):
        if cls is Competition:
            if isinstance(data, _UniqueTournamentData):
                return object().__new__(_TournamentCompetition)
            if isinstance(data, _UniqueStageData):
                return object().__new__(_StageCompetition)
            raise TypeError(f"Competition data must be either _UniqueTournamentData or _UniqueStageData, got {type(data)}")
        return super().__new__(cls)

    @property
    def id(self) -> str:
        """The unique ID of the competition."""
        return self.encode_id(self._data.id)

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

    @property
    @abstractmethod
    def seasons(self) -> EntityCollection[Season]:
        """Fetch all seasons for this competition."""
        raise NotImplementedError("Subclasses of Competition must implement the seasons property")

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


class _TournamentCompetition(Competition):
    _data: _UniqueTournamentData
    _PREFIX: str = "trnc"

    def __init__(self, data: _UniqueTournamentData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)
        if not isinstance(data, _UniqueTournamentData):
            raise TypeError(f"Tournament competition data must be of type _UniqueTournamentData, got {type(data)}")

    @cached_property
    def seasons(self) -> EntityCollection[Season]: # TODO - _TournamentSeason
        """Fetch all seasons for this tournament competition."""
        from .season import Season
        return EntityCollection([
            Season(s, self._provider, competition=self)
            for s in self._provider.get_unique_tournament_seasons(self._data.id)
        ])

    @staticmethod
    def _fetch_entity(raw_id: int, provider: SofascoreProvider, **kwargs) -> _UniqueTournamentData:
        """Fetch the unique tournament data from the provider by its raw ID."""
        try:
            return provider.get_unique_tournament(raw_id)
        except ProviderNotFoundError as e:
            logger.debug(f"Tournament with id {raw_id} not found: {e}")
            raise EntityNotFoundError(f"Tournament with id {raw_id} not found") from e
        except FetchError as e:
            logger.error(f"Network error while fetching tournament with id {raw_id}: {e}")
            raise DomainError(f"Network error while fetching tournament with id {raw_id}") from e


class _StageCompetition(Competition):
    _data: _UniqueStageData
    _PREFIX: str = "stgc"

    def __init__(self, data: _UniqueStageData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)
        if not isinstance(data, _UniqueStageData):
            raise TypeError(f"Stage competition data must be of type _UniqueStageData, got {type(data)}")

    @cached_property
    def seasons(self) -> EntityCollection[Season]: # TODO - _StageSeason
        """Fetch all seasons for this stage competition."""
        from .season import Season
        return EntityCollection([
            Season(s, self._provider, competition=self)
            for s in self._provider.get_unique_stage_seasons(self._data.id)
        ])

    @staticmethod
    def _fetch_entity(raw_id: int, provider: SofascoreProvider, **kwargs) -> _UniqueStageData:
        """Fetch the unique stage data from the provider by its raw ID."""
        try:
            us_seasons = provider.get_unique_stage_seasons(raw_id)
            if not us_seasons:
                raise ProviderNotFoundError(f"Unique stage with id {raw_id} not found")
            return us_seasons[0].unique_stage
        except ProviderNotFoundError as e:
            logger.debug(f"Unique stage with id {raw_id} not found: {e}")
            raise EntityNotFoundError(f"Unique stage with id {raw_id} not found") from e
        except FetchError as e:
            logger.error(f"Network error while fetching unique stage with id {raw_id}: {e}")
            raise DomainError(f"Network error while fetching unique stage with id {raw_id}") from e
