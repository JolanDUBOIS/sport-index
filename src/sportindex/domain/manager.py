from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Optional

from . import logger
from .base import IdentifiableEntity, EventAwareMixin, EntityCollection
from .utils import merge_dataclasses
from sportindex.provider.parsed import ParsedManager, ParsedManagerCareerHistoryItem
from sportindex.exceptions import EntityNotFoundError, DomainError, ValidationError, NotFoundError, FetchError

if TYPE_CHECKING:
    from .competitor import Competitor
    from .core import Country, Sport
    from .event import EventCollection
    from sportindex.provider.parsed import ParsedSofascoreProvider

ManagerCareerHistory = ParsedManagerCareerHistoryItem


class Manager(IdentifiableEntity[ParsedManager], EventAwareMixin):
    """A manager, e.g. 'Luis Enrique', 'Pep Guardiola', etc."""
    REPR_FIELDS = ("id", "name", "slug", "short_name", "sport", "country")

    def __init__(self, data: ParsedManager, provider: ParsedSofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, ParsedManager):
            raise ValidationError("Manager data must be of type ParsedManager")

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
        return self._data.shortName

    @cached_property
    def sport(self) -> Sport:
        """The sport this manager is associated with."""
        return Sport(self._data.sport, self._provider)

    @cached_property
    def country(self) -> Optional[Country]:
        """The country this manager is associated with, if any."""
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
    def performances(self) -> list[ManagerCareerHistory]:
        return self._provider.get_manager_career_history(self._data.id)

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Fetch all fixtures for this manager."""
        from .event import EventCollection
        if not silent:
            logger.warning("No fixtures endpoint available for managers, returning empty list")
        return EventCollection([])

    def get_results(self, silent: bool = False) -> EventCollection:
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
            self._data = merge_dataclasses(self._data, self._provider.get_manager(self._data.id))
            assert isinstance(self._data, ParsedManager)
            self._full_loaded = True
            self._clear_cache()
        except NotFoundError as e:
            from sportindex.exceptions import EntityNotFoundError
            raise EntityNotFoundError(f"Manager with id {self._data.id} not found during full load") from e
        except FetchError as e:
            from sportindex.exceptions import DomainError
            raise DomainError(f"Network error while fully loading manager with id {self._data.id}") from e

    def _clear_cache(self) -> None:
        """Clear cached properties."""
        self.__dict__.pop("sport", None)
        self.__dict__.pop("country", None)
        self.__dict__.pop("team", None)
        self.__dict__.pop("teams", None)
        self.__dict__.pop("performances", None)

    @classmethod
    def from_id(cls, manager_id: int, provider: ParsedSofascoreProvider) -> Manager:
        """Fetch a manager by its ID."""
        try:
            parsed_data = provider.get_manager(manager_id)
        except NotFoundError as e:
            raise EntityNotFoundError(f"Manager with id {manager_id} not found") from e
        except FetchError as e:
            raise DomainError(f"Network error while fetching manager {manager_id}") from e
        return cls(parsed_data, provider)

    @classmethod
    def search(cls, query: str, provider: ParsedSofascoreProvider) -> EntityCollection[Manager]:
        """Search for managers matching the given query (up to the first 20 matches)."""
        entities = []
        for page in range(51): # Sofascore has a maximum of 50 pages of search results
            matches = provider.search_managers(query=query, page=page)
            if not matches:
                break
            for item in matches:
                entities.append(Manager(item.entity, provider))
            if len(matches) > 20:
                break
        return EntityCollection(entities[:20])
