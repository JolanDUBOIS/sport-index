from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING

from pydantic import BaseModel

from sportindex.api_client.models import _RefereeData
from sportindex.exceptions import (
    DomainError,
    EntityNotFoundError,
    FetchError,
    ProviderNotFoundError,
)

from .base import SearchableMixin
from .event import EventAwareMixin

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
        id (str): Unique identifier of the referee.
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
    _PREFIX = "ref"
    _REPR_FIELDS = ("id", "name", "slug", "sport", "country")

    def __init__(self, data: _RefereeData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _RefereeData):
            raise TypeError(f"Referee data must be of type _RefereeData, got {type(data)}")

        self._full_loaded = False

    @property
    def id(self) -> str:
        """The unique ID of the referee."""
        return self.encode_id(self._data.id)

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
        return int(self._data.games) if self._data.games is not None else None

    @cached_property
    def cards(self) -> Cards | None:
        """Get the number of cards this referee has given."""
        self._full_load()
        if self._data.yellow_cards is None or self._data.red_cards is None or self._data.yellow_red_cards is None:
            return None
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

    @staticmethod
    def _fetch_entity(raw_id: int, provider: SofascoreProvider, **kwargs) -> _RefereeData:
        """Fetch the referee data from the provider by its raw ID."""
        try:
            return provider.get_referee(raw_id)
        except ProviderNotFoundError as e:
            logger.debug(f"Referee with id {raw_id} not found: {e}")
            raise EntityNotFoundError(f"Referee with id {raw_id} not found") from e
        except FetchError as e:
            logger.error(f"Network error while fetching referee with id {raw_id}: {e}")
            raise DomainError(f"Network error while fetching referee with id {raw_id}") from e

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
