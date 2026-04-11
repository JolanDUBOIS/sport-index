from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Optional, Self, Literal, overload

from . import logger
from .base import SearchableMixin
from .collections import EntityCollection, ScoredEntityCollection, EventCollection
from .event import EventAwareMixin
from .utils import merge_pydantic_models
from sportindex.exceptions import ProviderNotFoundError, FetchError, EntityNotFoundError, DomainError
from sportindex.provider.models import _VenueData, _StageData

if TYPE_CHECKING:
    from .competitor import Competitor
    from .core import Country
    from sportindex.provider import SofascoreProvider
    from sportindex.provider.models import BaseSchema


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
        elif isinstance(self._data, _StageData):
            return self._data.info.circuit if self._data.info else ""

    @property
    def city(self) -> Optional[str]:
        """The city where the venue is located."""
        self._full_load()
        if isinstance(self._data, _VenueData):
            return self._data.city.name if self._data.city else None
        elif isinstance(self._data, _StageData):
            return self._data.info.circuit_city if self._data.info else None

    @property
    def capacity(self) -> Optional[int]:
        """The capacity of the venue, if available."""
        if isinstance(self._data, _VenueData):
            self._full_load()
            return self._data.capacity or (self._data.stadium.capacity if self._data.stadium else None)
        elif isinstance(self._data, _StageData):
            return None

    @cached_property
    def country(self) -> Optional[Country]:
        """The country where the venue is located, if available."""
        self._full_load()
        from .core import Country
        if isinstance(self._data, _VenueData):
            return Country(self._data.country, self._provider)
        elif isinstance(self._data, _StageData):
            return Country.from_name(self._data.info.circuit_country, self._provider) if self._data.info and self._data.info.circuit_country else None

    @cached_property
    def teams(self) -> EntityCollection[Competitor]:
        self._full_load()
        from .competitor import Competitor
        if isinstance(self._data, _VenueData):
            return EntityCollection([
                Competitor(t, self._provider)
                for t in self._data.main_teams
            ])
        elif isinstance(self._data, _StageData):
            logger.warning("Teams for stages are not available in the current provider implementation, returning empty collection")
            return EntityCollection()

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Fetch all fixtures for this venue."""
        if isinstance(self._data, _VenueData):
            return self._fetch_paginated_events(self._provider.get_venue_fixtures, self._data.id)
        elif isinstance(self._data, _StageData):
            if not silent:
                logger.warning("Fixtures for stages are not available in the current provider implementation, returning empty collection")
            return EventCollection()

    def get_results(self, silent: bool = False) -> EventCollection:
        """Fetch all results for this venue."""
        if isinstance(self._data, _VenueData):
            return self._fetch_paginated_events(self._provider.get_venue_results, self._data.id)
        elif isinstance(self._data, _StageData):
            if not silent:
                logger.warning("Results for stages are not available in the current provider implementation, returning empty collection")
            return EventCollection()

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
        entity_data = cls._fetch_entity(venue_id, provider)
        
        instance = cls(entity_data, provider)
        if not issubclass(type(instance), cls):
            raise TypeError(
                f"ID {venue_id} belongs to a {type(instance).__name__}, but was initialized as a {cls.__name__}. "
                f"Use {type(instance).__name__}.from_id() instead."
            )
        return instance

    @classmethod
    def search(cls, query: str, provider: SofascoreProvider, max_results: int = 20) -> ScoredEntityCollection[Venue]:
        """
        Search for venues matching the given query, returning up to max_results results.
        Stage related venues (such as circuits) are not currently included in search results due to provider limitations.
        """
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
    def _fetch_entity(cls, venue_id: int, provider: SofascoreProvider, strict: Literal[False]) -> Optional[_VenueData | _StageData]: ...

    @classmethod
    def _fetch_entity(cls, venue_id: int, provider: SofascoreProvider, strict: bool = True) -> Optional[_VenueData | _StageData]:
        """Fetch the complete venue data from the provider by its ID."""
        raw_id, type_idx = cls.decode_id(venue_id)

        try:
            if type_idx == 1:
                return cls._fetch_raw_venue(raw_id, provider)
            elif type_idx == 2:
                return cls._fetch_raw_stage(raw_id, provider)
            else:
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
