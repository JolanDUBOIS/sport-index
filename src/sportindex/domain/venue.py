from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING, Literal, Self, overload

from sportindex.exceptions import (
    DomainError,
    EntityNotFoundError,
    FetchError,
    ProviderNotFoundError,
)
from sportindex.api_client.models import _StageData, _VenueData

from .base import SearchableMixin
from .collections import EntityCollection, EventCollection, ScoredEntityCollection
from .event import EventAwareMixin
from .utils import merge_pydantic_models

if TYPE_CHECKING:
    from sportindex.api_client import SofascoreProvider
    from sportindex.api_client.models import BaseSchema

    from .competitor import Competitor
    from .core import Country

logger = logging.getLogger(__name__)


class Venue(SearchableMixin, EventAwareMixin):
    """Represents a sports venue or race stage, e.g., a stadium, tennis court, or race track.

    Handles basic information, location, capacity, associated teams, and provides
    lazy full-loading for detailed API properties.

    Attributes:
        id (int): Unique identifier of the venue.
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
    _N_TYPES: int = 2
    _TYPE_MAP: dict[type[BaseSchema], int] = {_VenueData: 1, _StageData: 2}

    def __init__(self, data: _VenueData | _StageData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, (_VenueData, _StageData)):
            raise TypeError(f"Venue data must be either _VenueData or _StageData, got {type(data)}")

        self._full_loaded = False

    @property
    def id(self) -> int:
        """The unique ID of the venue."""
        type_idx = self._TYPE_MAP[type(self._data)]
        return self.encode_id(self._data.id, type_idx)

    @property
    def name(self) -> str:
        """The name of the venue."""
        if isinstance(self._data, _VenueData):
            return self._data.name or (self._data.stadium.name if self._data.stadium else "")
        if isinstance(self._data, _StageData):
            return self._data.info.circuit if self._data.info else ""
        raise TypeError(f"Cannot determine name for data type: {type(self._data).__name__}")

    @property
    def city(self) -> str | None:
        """The city where the venue is located."""
        self._full_load()
        if isinstance(self._data, _VenueData):
            return self._data.city.name if self._data.city else None
        if isinstance(self._data, _StageData):
            return self._data.info.circuit_city if self._data.info else None
        raise TypeError(f"Cannot determine city for data type: {type(self._data).__name__}")

    @property
    def capacity(self) -> int | None:
        """The capacity of the venue, if available."""
        if isinstance(self._data, _VenueData):
            self._full_load()
            return self._data.capacity or (self._data.stadium.capacity if self._data.stadium else None)
        if isinstance(self._data, _StageData):
            return None
        raise TypeError(f"Cannot determine capacity for data type: {type(self._data).__name__}")

    @cached_property
    def country(self) -> Country | None:
        """The country where the venue is located, if available."""
        self._full_load()
        from .core import Country
        if isinstance(self._data, _VenueData):
            return Country(self._data.country, self._provider)
        if isinstance(self._data, _StageData):
            return Country.from_name(self._data.info.circuit_country, self._provider) if self._data.info and self._data.info.circuit_country else None
        raise TypeError(f"Cannot determine country for data type: {type(self._data).__name__}")

    @cached_property
    def teams(self) -> EntityCollection[Competitor]:
        self._full_load()
        from .competitor import Competitor
        if isinstance(self._data, _VenueData):
            return EntityCollection([
                Competitor(t, self._provider)
                for t in self._data.main_teams
            ])
        if isinstance(self._data, _StageData):
            logger.warning("Teams for stages are not available in the current provider implementation, returning empty collection")
            return EntityCollection()
        raise TypeError(f"Cannot determine teams for data type: {type(self._data).__name__}")

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Fetch all fixtures for this venue."""
        if isinstance(self._data, _VenueData):
            return self._fetch_paginated_events(self._provider.get_venue_fixtures, self._data.id)
        if isinstance(self._data, _StageData):
            if not silent:
                logger.warning("Fixtures for stages are not available in the current provider implementation, returning empty collection")
            return EventCollection()
        raise TypeError(f"Cannot fetch fixtures for data type: {type(self._data).__name__}")

    def get_results(self, silent: bool = False) -> EventCollection:
        """Fetch all results for this venue."""
        if isinstance(self._data, _VenueData):
            return self._fetch_paginated_events(self._provider.get_venue_results, self._data.id)
        if isinstance(self._data, _StageData):
            if not silent:
                logger.warning("Results for stages are not available in the current provider implementation, returning empty collection")
            return EventCollection()
        raise TypeError(f"Cannot fetch results for data type: {type(self._data).__name__}")

    def _full_load(self) -> None:
        """
        Lazy-loads the complete venue from the provider.
        Called automatically when accessing properties that require full details
        missing from the initial lightweight API response.
        """
        if self._full_loaded:
            return
        try:
            self._data = merge_pydantic_models(self._data, self._provider.get_venue(self._data.id))
        except ProviderNotFoundError:
            logger.debug(f"Venue with id {self._data.id} not found during full load")
        except FetchError as e:
            logger.debug(f"Network error while fully loading venue with id {self._data.id}: {e}")
        self._full_loaded = True
        self._clear_cache()

    @classmethod
    def from_id(cls, venue_id: int, provider: SofascoreProvider) -> Self:
        """Fetch a venue by its ID."""
        if not isinstance(venue_id, int):
            raise TypeError(f"Venue ID must be an integer, got {type(venue_id)}")

        try:
            entity_data = cls._fetch_entity(venue_id, provider)
            instance = cls(entity_data, provider)
            if not issubclass(type(instance), cls):
                raise TypeError(
                    f"ID {venue_id} belongs to a {type(instance).__name__}, but was initialized as a {cls.__name__}. "
                    f"Use {type(instance).__name__}.from_id() instead."
                )
            return instance
        except ProviderNotFoundError as e:
            raise EntityNotFoundError(f"Venue with id {venue_id} not found") from e
        except FetchError as e:
            raise DomainError(f"Network error while fetching venue with id {venue_id}") from e

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

    @overload
    @classmethod
    def _fetch_entity(cls, venue_id: int, provider: SofascoreProvider, strict: Literal[True] = True) -> _VenueData | _StageData: ...

    @overload
    @classmethod
    def _fetch_entity(cls, venue_id: int, provider: SofascoreProvider, strict: Literal[False]) -> _VenueData | _StageData | None: ...

    @classmethod
    def _fetch_entity(cls, venue_id: int, provider: SofascoreProvider, strict: bool = True) -> _VenueData | _StageData | None:
        """Fetch the complete venue data from the provider by its ID."""
        raw_id, type_idx = cls.decode_id(venue_id)

        try:
            if type_idx == 1:
                return cls._fetch_raw_venue(raw_id, provider)
            if type_idx == 2:
                return cls._fetch_raw_stage(raw_id, provider)
            raise TypeError(f"Invalid venue ID {venue_id}: unknown type index {type_idx}")

        except ProviderNotFoundError:
            logger.debug(f"Venue with ID {venue_id} not found during fetch")
            if strict:
                raise EntityNotFoundError(f"Venue with ID {venue_id} not found during fetch") from None

        except FetchError as e:
            logger.debug(f"Network error while fetching venue with ID {venue_id}: {e}")
            if strict:
                raise DomainError(f"Network error while fetching venue with ID {venue_id}") from e

        return None

    @staticmethod
    def _fetch_raw_venue(venue_id: int, provider: SofascoreProvider) -> _VenueData:
        """Fetch _VenueData by its ID."""
        return provider.get_venue(venue_id)

    @staticmethod
    def _fetch_raw_stage(stage_id: int, provider: SofascoreProvider) -> _StageData:
        """Fetch _StageData by its ID."""
        return provider.get_stage(stage_id)
