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
    """Represents a sports venue or race stage, e.g., a stadium, tennis court, or race track.

    Handles basic information, location, capacity, associated teams, and provides
    lazy full-loading for detailed API properties.

    Attributes:
        id (str): Unique identifier of the venue.
        name (str): Name of the venue.
        city (str | None): City where the venue is located.
        capacity (int | None): Seating or attendance capacity of the venue.
        country (Country | None): Country where the venue is located.
        teams (EntityCollection[Competitor]): Main teams associated with the venue.

    Methods:
        get_fixtures() -> EventCollection:
            Fetch all fixtures scheduled at this venue.
        get_results() -> EventCollection:
            Fetch all results played at this venue.
        from_id(venue_id: int, provider: SofascoreProvider) -> Venue:
            Fetch a venue by its unique ID.
        search(query: str, provider: SofascoreProvider) -> ScoredEntityCollection[Venue]:
            Search for venues by query string (up to 20 results).
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
                return object().__new__(_StdVenue)
            if isinstance(data, _StageData):
                return object().__new__(_StageVenue)
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
