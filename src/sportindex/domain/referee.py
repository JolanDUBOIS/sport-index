from __future__ import annotations

from functools import cached_property
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from . import logger
from .base import IdentifiableEntity, EventAwareMixin, EntityCollection
from .utils import merge_dataclasses
from sportindex.exceptions import ProviderNotFoundError, FetchError, EntityNotFoundError, DomainError
from sportindex.provider.parsed import ParsedReferee

if TYPE_CHECKING:
    from .core import Country, Sport
    from .event import EventCollection
    from sportindex.provider.parsed import ParsedSofascoreProvider


class Referee(IdentifiableEntity[ParsedReferee], EventAwareMixin):
    """A referee, e.g. 'Pierluigi Collina', 'Michael Masi', etc."""
    REPR_FIELDS = ("id", "name", "slug", "sport", "country")

    def __init__(self, data: ParsedReferee, provider: ParsedSofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, ParsedReferee):
            raise TypeError("Referee data must be of type ParsedReferee")

        self._full_loaded = False

    @property
    def id(self) -> int:
        """The unique ID of the referee."""
        return self._data.id

    @property
    def name(self) -> str:
        """The full name of the referee."""
        return self._data.name

    @property
    def slug(self) -> str:
        """The slug of the referee (used in URLs)."""
        return self._data.slug or self._data.name.lower().replace(" ", "-")

    @cached_property
    def sport(self) -> Sport:
        """The sport this referee is associated with."""
        return Sport(self._data.sport, self._provider)

    @cached_property
    def country(self) -> Optional[Country]:
        """The country this referee is associated with, if any."""
        return Country(self._data.country, self._provider) if self._data.country else None

    @cached_property
    def games(self) -> Optional[int]:
        """Get the number of games this referee has officiated."""
        self._full_load()
        return int(self._data.games)

    @cached_property
    def cards(self) -> Optional[Cards]:
        """Get the number of cards this referee has given."""
        self._full_load()
        return Cards(
            yellow=int(self._data.yellowCards),
            red=int(self._data.redCards),
            yellow_red=int(self._data.yellowRedCards)
        )

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Fetch all fixtures for this referee."""
        from .event import EventCollection
        if not silent:
            logger.warning("No fixtures endpoint available for referees, returning empty list")
        return EventCollection([])

    def get_results(self, silent: bool = False) -> EventCollection:
        """Fetch all results for this referee."""
        return self._fetch_paginated_events(self._provider.get_referee_results, self._data.id)

    def _full_load(self) -> None:
        """
        Lazy-loads the complete referee from the provider.
        Called automatically when accessing properties that require full details 
        missing from the initial lightweight API response.
        """
        if self._full_loaded:
            return
        try:
            self._data = merge_dataclasses(self._data, self._provider.get_referee(self._data.id))
            if not isinstance(self._data, ParsedReferee):
                raise TypeError("Referee data must be of type ParsedReferee after full load")
            self._full_loaded = True
            self._clear_cache()
        except ProviderNotFoundError as e:
            raise EntityNotFoundError(f"Referee with id {self._data.id} not found during full load") from e
        except FetchError as e:
            raise DomainError(f"Network error while fully loading referee with id {self._data.id}") from e

    def _clear_cache(self) -> None:
        """Clear cached properties."""
        self.__dict__.pop("sport", None)
        self.__dict__.pop("country", None)
        self.__dict__.pop("games", None)
        self.__dict__.pop("cards", None)

    @classmethod
    def from_id(cls, referee_id: int, provider: ParsedSofascoreProvider) -> Referee:
        """Fetch a referee by its ID."""
        try:
            parsed_data = provider.get_referee(referee_id)
        except ProviderNotFoundError as e:
            raise EntityNotFoundError(f"Referee with id {referee_id} not found") from e
        except FetchError as e:
            raise DomainError(f"Network error while fetching referee {referee_id}") from e
        return cls(parsed_data, provider)

    @classmethod
    def search(cls, query: str, provider: ParsedSofascoreProvider) -> EntityCollection[Referee]:
        """Search for referees matching the given query (up to the first 20 matches)."""
        entities = []
        for page in range(51): # Sofascore has a maximum of 50 pages of search results
            matches = provider.search_referees(query=query, page=page)
            if not matches:
                break
            for item in matches:
                entities.append(Referee(item.entity, provider))
            if len(matches) > 20:
                break
        return EntityCollection(entities[:20])


@dataclass(frozen=True)
class Cards:
    yellow: int
    red: int
    yellow_red: int
