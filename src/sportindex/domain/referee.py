from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING, Self

from pydantic import BaseModel

from sportindex.exceptions import (
    DomainError,
    EntityNotFoundError,
    FetchError,
    ProviderNotFoundError,
)
from sportindex.api_client.models import _RefereeData

from .base import SearchableMixin
from .event import EventAwareMixin
from .utils import merge_pydantic_models

if TYPE_CHECKING:
    from sportindex.api_client import SofascoreProvider

    from .collections import ScoredEntityCollection
    from .core import Country, Sport
    from .event import EventCollection

logger = logging.getLogger(__name__)


class Cards(BaseModel):
    """Represents the count of different types of cards issued by a referee."""
    yellow: int
    red: int
    yellow_red: int


class Referee(SearchableMixin, EventAwareMixin):
    """Represents a sports referee/officiator (e.g., football referee, Formula 1 race director).

    Handles basic information, associated sport and country, games officiated,
    and cards issued. Supports lazy full-loading for properties requiring
    detailed API responses.

    Attributes:
        id (int): Unique identifier of the referee.
        name (str): Full name of the referee.
        slug (str): URL-friendly slug of the referee.
        sport (Sport): Sport associated with the referee.
        country (Country | None): Country associated with the referee, if available.
        games (int | None): Number of games officiated by the referee.
        cards (Cards | None): Counts of yellow, red, and yellow-red cards issued.

    Methods:
        get_fixtures(silent: bool = False) -> EventCollection:
            Returns fixtures for this referee. Currently returns empty, logs a warning.
        get_results(silent: bool = False) -> EventCollection:
            Returns results for this referee.
        from_id(referee_id: int, provider: SofascoreProvider) -> Referee:
            Fetch a referee by its unique ID.
        search(query: str, provider: SofascoreProvider) -> ScoredEntityCollection[Referee]:
            Search for referees matching a query string (up to 20 results).
    """
    _data: _RefereeData
    _REPR_FIELDS = ("id", "name", "slug", "sport", "country")

    def __init__(self, data: _RefereeData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _RefereeData):
            raise TypeError(f"Referee data must be of type _RefereeData, got {type(data)}")

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
        from .core import Sport
        return Sport(self._data.sport, self._provider)

    @cached_property
    def country(self) -> Country | None:
        """The country this referee is associated with, if any."""
        from .core import Country
        return Country(self._data.country, self._provider) if self._data.country else None

    @cached_property
    def games(self) -> int | None:
        """Get the number of games this referee has officiated."""
        self._full_load()
        return int(self._data.games)

    @cached_property
    def cards(self) -> Cards | None:
        """Get the number of cards this referee has given."""
        self._full_load()
        return Cards(
            yellow=int(self._data.yellow_cards),
            red=int(self._data.red_cards),
            yellow_red=int(self._data.yellow_red_cards)
        )

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Fetch all fixtures for this referee."""
        from .event import EventCollection
        if not silent:
            logger.warning("No fixtures endpoint available for referees, returning empty list")
        return EventCollection()

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
            self._data = merge_pydantic_models(self._data, self._provider.get_referee(self._data.id))
        except ProviderNotFoundError:
            logger.debug(f"Referee with id {self._data.id} not found during full load")
        except FetchError as e:
            logger.debug(f"Network error while fully loading referee with id {self._data.id}: {e}")
        self._full_loaded = True
        self._clear_cache()

    @classmethod
    def from_id(cls, referee_id: int, provider: SofascoreProvider) -> Self:
        """Fetch a referee by its ID."""
        try:
            parsed_data = provider.get_referee(referee_id)
            return cls(parsed_data, provider)
        except ProviderNotFoundError as e:
            raise EntityNotFoundError(f"Referee with id {referee_id} not found") from e
        except FetchError as e:
            raise DomainError(f"Network error while fetching referee {referee_id}") from e

    @classmethod
    def search(cls, query: str, provider: SofascoreProvider, max_results: int = 20) -> ScoredEntityCollection[Referee]:
        """Search for referees matching the given query, returning up to max_results results."""
        cls._validate_query(query)
        return cls._paginate_search(
            query=query,
            provider=provider,
            search_func=provider.search_referees,
            max_results=max_results
        )
