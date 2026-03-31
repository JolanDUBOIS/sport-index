from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Optional

from . import logger
from .base import IdentifiableEntity, EventAwareMixin, EntityCollection
from .utils import merge_pydantic_models
from sportindex.exceptions import ProviderNotFoundError, FetchError, EntityNotFoundError, DomainError
from sportindex.provider.models import _VenueData, _StageData

if TYPE_CHECKING:
    from .core import Country
    from .event import EventCollection
    from .competitor import Competitor
    from sportindex.provider import SofascoreProvider


class Venue(IdentifiableEntity[_VenueData | _StageData], EventAwareMixin):
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
        search(query: str, provider: SofascoreProvider) -> EntityCollection[Venue]:
            Search for venues by query string (up to 20 results).
    """
    _REPR_FIELDS = ("id", "name")

    def __init__(self, data: _VenueData | _StageData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, (_VenueData, _StageData)):
            raise TypeError(f"Venue data must be either _VenueData or _StageData, got {type(data)}")

        self._full_loaded = False

    @property
    def id(self) -> int:
        """The unique ID of the venue."""
        return self._data.id

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
            return self._data.city
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
        if isinstance(self._data, _VenueData):
            return Country(self._data.country, self._provider)
        elif isinstance(self._data, _StageData):
            return Country.from_name(self._data.info.circuit_country) if self._data.info and self._data.info.circuit_country else None

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
            logger.warning("Teams for stages are not available in the current provider implementation, returning empty list")
            return EntityCollection([])

    def get_fixtures(self) -> EventCollection:
        """Fetch all fixtures for this venue."""
        return self._fetch_paginated_events(self._provider.get_venue_fixtures, self._data.id)

    def get_results(self) -> EventCollection:
        """Fetch all results for this venue."""
        return self._fetch_paginated_events(self._provider.get_venue_results, self._data.id)

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
            if not isinstance(self._data, _VenueData):
                raise TypeError(f"Venue data must be of type _VenueData after full load, got {type(self._data)}")
            self._full_loaded = True
            self._clear_cache()
        except ProviderNotFoundError:
            logger.debug(f"Venue with id {self._data.id} not found during full load")
            self._full_loaded = True
            self._clear_cache()
        except FetchError as e:
            logger.debug(f"Network error while fully loading venue with id {self._data.id}: {e}")
            self._full_loaded = True
            self._clear_cache()

    def _clear_cache(self) -> None:
        """Clear cached properties."""
        self.__dict__.pop("country", None)
        self.__dict__.pop("teams", None)
    @classmethod
    def from_id(cls, venue_id: int, provider: SofascoreProvider) -> Venue:
        """Fetch a venue by its ID."""
        try:
            parsed_data = provider.get_venue(venue_id)
        except ProviderNotFoundError as e:
            raise EntityNotFoundError(f"Venue with id {venue_id} not found") from e
        except FetchError as e:
            raise DomainError(f"Network error while fetching venue {venue_id}") from e
        return cls(parsed_data, provider)

    @classmethod
    def search(cls, query: str, provider: SofascoreProvider) -> EntityCollection[Venue]:
        """Search for venues matching the given query (up to the first 20 matches)."""
        entities = []
        for page in range(51): # Sofascore has a maximum of 50 pages of search results
            matches = provider.search_venues(query=query, page=page)
            if not matches:
                break
            for item in matches:
                entities.append(Venue(item.entity, provider))
            if len(matches) > 20:
                break
        return EntityCollection(entities[:20])
