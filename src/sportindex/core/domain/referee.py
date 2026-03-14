from __future__ import annotations

from functools import cached_property
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Optional

from . import logger
from .base import BaseEntity, EventAwareMixin
from sportindex.core.provider.parsed import ParsedReferee

if TYPE_CHECKING:
    from .core import Country, Sport
    from .event import EventCollection
    from sportindex.core.provider.parsed import ParsedSofascoreProvider


class Referee(BaseEntity[ParsedReferee], EventAwareMixin):
    """A referee, e.g. 'Pierluigi Collina', 'Michael Masi', etc."""
    REPR_FIELDS = ("id", "name", "slug", "sport", "country")

    def __init__(self, data: ParsedReferee, provider: ParsedSofascoreProvider | None = None, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, ParsedReferee):
            raise ValueError("Referee data must be of type ParsedReferee")

        self._full_loaded = False

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
        return self._fetch_paginated_events(self._provider.get_referee_results, self.id)

    def _full_load(self) -> None:
        """
        Lazy-loads the complete referee from the provider.
        Called automatically when accessing properties that require full details 
        missing from the initial lightweight API response.
        """
        if self._full_loaded:
            return
        try:
            self._data = replace(self._data, **vars(self._provider.get_referee(self.id)))
            assert isinstance(self._data, ParsedReferee)
            self._full_loaded = True
            self._clear_cache()
        except Exception:
            logger.exception(f"Failed to fully load referee with id {self.id}.")

    def _clear_cache(self) -> None:
        """Clear cached properties."""
        self.__dict__.pop("sport", None)
        self.__dict__.pop("country", None)
        self.__dict__.pop("games", None)
        self.__dict__.pop("cards", None)


@dataclass(frozen=True)
class Cards:
    yellow: int
    red: int
    yellow_red: int
