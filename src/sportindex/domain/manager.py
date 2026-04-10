from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Optional, Self

from . import logger
from .base import IdentifiableEntity, EntityCollection, SearchableMixin
from .event import Event, EventAwareMixin
from .utils import merge_pydantic_models
from sportindex.exceptions import EntityNotFoundError, DomainError, ProviderNotFoundError, FetchError
from sportindex.provider.models import _ManagerData, ManagerTenure as _ManagerTenure

if TYPE_CHECKING:
    from .competitor import Competitor
    from .core import Country, Sport
    from .event import EventCollection
    from sportindex.provider import SofascoreProvider


class ManagerTenure(_ManagerTenure):
    team: Competitor

    @classmethod
    def _from_base_schema(cls, data: _ManagerTenure, provider: SofascoreProvider) -> ManagerTenure:
        from .competitor import Competitor
        return cls(
            **data.model_dump(by_alias=True, exclude={"team"}),
            team=Competitor(data.team, provider)
        )


class Manager(IdentifiableEntity, EventAwareMixin[Event], SearchableMixin):
    """Represents a sports manager/coach (e.g., football manager, Formula 1 team principal).

    This entity handles basic information, associated sport and country, team affiliations,
    career history, and provides access to fixtures and results. Supports lazy full-loading
    for properties that require more detailed API responses.

    Attributes:
        id (int): Unique identifier of the manager.
        name (str): Full name of the manager.
        slug (str): URL-friendly slug of the manager.
        short_name (str): Shortened name or abbreviation (e.g., "Z. Zidane").
        sport (Sport): Sport associated with the manager.
        country (Country | None): Country associated with the manager, if available.
        team (Competitor | None): Current primary team, if assigned.
        teams (EntityCollection[Competitor]): All teams associated with the manager.
        performances (list[ManagerTenure]): Career history and performance records of the manager.

    Methods:
        get_fixtures(silent: bool = False) -> EventCollection:
            Returns fixtures for this manager. Currently returns empty, logs a warning.
        get_results(silent: bool = False) -> EventCollection:
            Returns results for this manager.
        from_id(manager_id: int, provider: SofascoreProvider) -> Manager:
            Fetch a manager by its unique ID.
        search(query: str, provider: SofascoreProvider) -> EntityCollection[Manager]:
            Search for managers matching a query string (up to 20 results).
    """
    _data: _ManagerData
    _REPR_FIELDS = ("id", "name", "slug", "short_name", "sport", "country")

    def __init__(self, data: _ManagerData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _ManagerData):
            raise TypeError(f"Manager data must be of type _ManagerData, got {type(data)}")

        self._full_loaded = False

    @property
    def id(self) -> int:
        """The unique ID of the manager."""
        return self._data.id

    @property
    def name(self) -> str:
        """The full name of the manager."""
        return self._data.name

    @property
    def slug(self) -> str:
        """The slug of the manager (used in URLs)."""
        return self._data.slug or self._data.name.lower().replace(" ", "-")

    @property
    def short_name(self) -> str:
        """The short name of the manager, e.g. "Z. Zidane"."""
        return self._data.short_name

    @cached_property
    def sport(self) -> Sport:
        """The sport this manager is associated with."""
        from .core import Sport
        return Sport(self._data.sport, self._provider)

    @cached_property
    def country(self) -> Optional[Country]:
        """The country this manager is associated with, if any."""
        from .core import Country
        return Country(self._data.country, self._provider) if self._data.country else None

    @cached_property
    def team(self) -> Optional[Competitor]:
        self._full_load()
        from .competitor import Competitor
        return Competitor(self._data.team, self._provider) if self._data.team else None

    @cached_property
    def teams(self) -> EntityCollection[Competitor]:
        self._full_load()
        from .competitor import Competitor
        return EntityCollection([Competitor(t, self._provider) for t in self._data.teams]) if self._data.teams else EntityCollection([])

    @cached_property
    def performances(self) -> list[ManagerTenure]:
        parsed_career_history = self._provider.get_manager_career_history(self._data.id)
        return [ManagerTenure._from_base_schema(parsed, provider=self._provider) for parsed in parsed_career_history]

    def get_fixtures(self, silent: bool = False) -> EventCollection[Event]:
        """Fetch all fixtures for this manager."""
        from .event import EventCollection
        if not silent:
            logger.warning("No fixtures endpoint available for managers, returning empty list")
        return EventCollection([])

    def get_results(self, silent: bool = False) -> EventCollection[Event]:
        """Fetch all results for this manager."""
        return self._fetch_paginated_events(self._provider.get_manager_results, self._data.id)

    def _full_load(self) -> None:
        """
        Lazy-loads the complete manager from the provider.
        Called automatically when accessing properties that require full details 
        missing from the initial lightweight API response.
        """
        if self._full_loaded:
            return
        try:
            self._data = merge_pydantic_models(self._data, self._provider.get_manager(self._data.id))
        except ProviderNotFoundError:
            logger.debug(f"Manager with id {self._data.id} not found during full load")
        except FetchError as e:
            logger.debug(f"Network error while fully loading manager with id {self._data.id}: {e}")
        self._full_loaded = True
        self._clear_cache()

    @classmethod
    def from_id(cls, manager_id: int, provider: SofascoreProvider) -> Self:
        """Fetch a manager by its ID."""
        try:
            parsed_data = provider.get_manager(manager_id)
        except ProviderNotFoundError as e:
            raise EntityNotFoundError(f"Manager with id {manager_id} not found") from e
        except FetchError as e:
            raise DomainError(f"Network error while fetching manager {manager_id}") from e
        return cls(parsed_data, provider)

    @classmethod
    def search(cls, query: str, provider: SofascoreProvider, max_results: int = 20) -> EntityCollection[Manager]:
        """Search for managers matching the given query, returning up to max_results results."""
        return cls._paginate_search(
            query=query,
            provider=provider,
            search_func=provider.search_managers,
            max_results=max_results
        )
