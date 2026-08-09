from __future__ import annotations

import logging
from abc import abstractmethod
from functools import cached_property
from typing import TYPE_CHECKING, overload

from sportindex.api_client.models import _StageData, _VenueData
from sportindex.exceptions import (
    DomainError,
    EntityNotFoundError,
    FetchError,
    ProviderNotFoundError,
)

from .base import SearchableMixin
from .collections import EntityCollection, EventCollection, ScoredEntityCollection
from .event import EventAwareMixin

if TYPE_CHECKING:
    from sportindex.api_client import SofascoreProvider

    from .competitor import Competitor
    from .core import Country

logger = logging.getLogger(__name__)


class Venue(SearchableMixin, EventAwareMixin):
    """Where an event takes place — a stadium, an arena, a circuit.

    Instantiating `Venue` returns one of two private variants depending on the payload: a
    standard venue, or a circuit derived from a stage. The circuit variant is far thinner —
    the provider exposes no capacity, no resident teams and no calendar for it — and those
    differences are noted per member below.

    Attributes:
        id (str): Globally unique SDK ID — "vnu:<id>" for standard venues, "stgv:<id>" for
            circuits.
        name (str): Venue name, e.g. "Parc des Princes", "Circuit de Monaco". Empty string
            when the provider names none.
        city (str | None): The city the venue is in, if the provider states it.
        capacity (int | None): How many spectators the venue holds, if the provider states
            it. Always None for circuits.
        country (Country | None): The country the venue is in, if the provider states it.
        teams (EntityCollection[Competitor]): The teams that call this venue home. Always
            empty for circuits.
        source (_VenueData | _StageData): The parsed payload backing this entity.
            (inherited from BaseEntity)

    Methods:
        get_fixtures(silent: bool = False) -> EventCollection: Events scheduled at this venue.
            Always empty for circuits — the provider offers no such endpoint. Logs a warning
            in that case unless `silent` is True.
        get_results(silent: bool = False) -> EventCollection: Events already played at this
            venue. Always empty for circuits, with the same warning behaviour.
        get_events() -> EventCollection: Fixtures and results combined, sorted by start time.
            (inherited from EventAwareMixin)
        search(query: str, provider: SofascoreProvider, max_results: int = 20) -> ScoredEntityCollection[Venue]:
            Venues matching `query`, each with its relevance score, capped at `max_results`.
            Circuits are never returned: the provider does not index them. (classmethod)
        from_id(entity_id: str, provider: SofascoreProvider) -> Venue: The venue with this SDK
            ID; the prefix decides which variant is built. (classmethod, inherited from
            IdentifiableEntity)

    Raises:
        TypeError: If constructed with data that is neither `_VenueData` nor `_StageData`.
        ValueError: If `search` is given an empty query.
        EntityNotFoundError: If `from_id` names a venue the provider does not have.
        DomainError: If the provider fails with a network or transport error.
    """
    _data: _VenueData | _StageData
    _REPR_FIELDS = ("id", "name")

    @overload
    def __new__(cls, data: _VenueData, provider: SofascoreProvider, **kwargs) -> _StdVenue: ...

    @overload
    def __new__(cls, data: _StageData, provider: SofascoreProvider, **kwargs) -> _StageVenue: ...

    def __new__(cls, data: _VenueData | _StageData, provider: SofascoreProvider, **kwargs):
        if cls is Venue:
            if isinstance(data, _VenueData):
                return super().__new__(_StdVenue)
            if isinstance(data, _StageData):
                return super().__new__(_StageVenue)
            raise TypeError(f"Venue data must be either _VenueData or _StageData, got {type(data)}")
        return super().__new__(cls)

    @property
    def id(self) -> str:
        """The unique ID of the venue."""
        return self.encode_id(self._data.id)

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the venue."""
        raise NotImplementedError("Subclasses must implement the 'name' property")

    @property
    @abstractmethod
    def city(self) -> str | None:
        """The city where the venue is located, if available."""
        raise NotImplementedError("Subclasses must implement the 'city' property")

    @property
    @abstractmethod
    def capacity(self) -> int | None:
        """The capacity of the venue, if available."""
        raise NotImplementedError("Subclasses must implement the 'capacity' property")

    @property
    @abstractmethod
    def country(self) -> Country | None:
        """The country where the venue is located, if available."""
        raise NotImplementedError("Subclasses must implement the 'country' property")

    @property
    @abstractmethod
    def teams(self) -> EntityCollection[Competitor]:
        """The main teams associated with the venue."""
        raise NotImplementedError("Subclasses must implement the 'teams' property")

    @classmethod
    def search(cls, query: str, provider: SofascoreProvider, max_results: int = 20) -> ScoredEntityCollection[Venue]:
        """
        Search for venues matching the given query, returning up to max_results results.
        Stage related venues (such as circuits) are not currently included in search results due to provider limitations.
        """
        cls._validate_query(query)
        return cls._paginate_search(
            query=query,
            provider=provider,
            search_func=provider.search_venues,
            max_results=max_results
        )


class _StdVenue(Venue):
    """Private `Venue` variant for standard venues such as stadiums and arenas; see `Venue`."""
    _PREFIX: str = "vnu"

    @property
    def name(self) -> str:
        """The name of the venue."""
        return self._data.name or (self._data.stadium.name if self._data.stadium else "")

    @property
    def city(self) -> str | None:
        """The city where the venue is located, if available."""
        return self._data.city.name if self._data.city else None

    @property
    def capacity(self) -> int | None:
        """The capacity of the venue, if available."""
        self._full_load()
        return self._data.capacity or (self._data.stadium.capacity if self._data.stadium else None)

    @cached_property
    def country(self) -> Country | None:
        """The country where the venue is located, if available."""
        self._full_load()
        from .core import Country
        return Country(self._data.country, self._provider) if self._data.country else None

    @cached_property
    def teams(self) -> EntityCollection[Competitor]:
        """The main teams associated with the venue."""
        self._full_load()
        from .competitor import Competitor
        return EntityCollection([
            Competitor(t, self._provider)
            for t in self._data.main_teams
        ])

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Fetch all fixtures for this venue."""
        return self._fetch_paginated_events(self._provider.get_venue_fixtures, self._data.id)

    def get_results(self, silent: bool = False) -> EventCollection:
        """Fetch all results for this venue."""
        return self._fetch_paginated_events(self._provider.get_venue_results, self._data.id)

    @staticmethod
    def _fetch_entity(raw_id: int, provider: SofascoreProvider, **kwargs) -> _VenueData:
        """Fetch the venue data from the provider by its raw ID."""
        try:
            return provider.get_venue(raw_id)
        except ProviderNotFoundError as e:
            logger.debug(f"Venue with ID {raw_id} not found: {e}")
            raise EntityNotFoundError(f"Venue with ID {raw_id} not found") from e
        except FetchError as e:
            logger.error(f"Network error while fetching venue with ID {raw_id}: {e}")
            raise DomainError(f"Network error while fetching venue with ID {raw_id}") from e


class _StageVenue(Venue):
    """Private `Venue` variant for circuits and courses derived from a stage; see `Venue`."""
    _PREFIX: str = "stgv"

    @property
    def name(self) -> str:
        """The name of the venue."""
        return self._data.info.circuit if self._data.info else ""

    @property
    def city(self) -> str | None:
        """The city where the venue is located, if available."""
        return self._data.info.circuit_city if self._data.info else None

    @property
    def capacity(self) -> int | None:
        """The capacity of the venue, if available."""
        return None

    @cached_property
    def country(self) -> Country | None:
        """The country where the venue is located, if available."""
        from .core import Country
        return Country.from_name(self._data.info.circuit_country, self._provider) if self._data.info and self._data.info.circuit_country else None

    @cached_property
    def teams(self) -> EntityCollection[Competitor]:
        """The main teams associated with the venue."""
        logger.warning("Teams for stages are not available in the current provider implementation, returning empty collection")
        return EntityCollection()

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Fetch all fixtures for this venue."""
        if not silent:
            logger.warning("Fixtures for stages are not available in the current provider implementation, returning empty collection")
        return EventCollection()

    def get_results(self, silent: bool = False) -> EventCollection:
        """Fetch all results for this venue."""
        if not silent:
            logger.warning("Results for stages are not available in the current provider implementation, returning empty collection")
        return EventCollection()

    @staticmethod
    def _fetch_entity(raw_id: int, provider: SofascoreProvider, **kwargs) -> _StageData:
        """Fetch the stage data from the provider by its raw ID."""
        try:
            return provider.get_stage(raw_id)
        except ProviderNotFoundError as e:
            logger.debug(f"Stage with ID {raw_id} not found: {e}")
            raise EntityNotFoundError(f"Stage with ID {raw_id} not found") from e
        except FetchError as e:
            logger.error(f"Network error while fetching stage with ID {raw_id}: {e}")
            raise DomainError(f"Network error while fetching stage with ID {raw_id}") from e
