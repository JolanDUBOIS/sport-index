from __future__ import annotations

from functools import cached_property
from dataclasses import replace
from datetime import datetime, date
from typing import TYPE_CHECKING, Optional

from . import logger
from .base import BaseEntity
from sportindex.core.provider.parsed import ParsedManager

if TYPE_CHECKING:
    from .competitor import Competitor
    from .core import Country, Sport
    from .event import Event
    from sportindex.core.provider.parsed import (
        ParsedSofascoreProvider,
        ParsedManagerCareerHistoryItem
    )


class Manager(BaseEntity[ParsedManager]):
    """A manager, e.g. 'Luis Enrique', 'Pep Guardiola', etc."""
    REPR_FIELDS = ("id", "name", "slug", "short_name", "sport", "country")

    def __init__(self, data: ParsedManager, provider: ParsedSofascoreProvider | None = None, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, ParsedManager):
            raise ValueError("Manager data must be of type ParsedManager")

        self._full_loaded = False

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
    def teams(self) -> list[Competitor]:
        self._full_load()
        from .competitor import Competitor
        return [Competitor(t, self._provider) for t in self._data.teams] if self._data.teams else []

    @cached_property
    def performances(self) -> list[ParsedManagerCareerHistoryItem]:
        return self._provider.get_manager_career_history(self.id)

    def get_fixtures(self) -> list[Event]:
        """Fetch all fixtures for this manager."""
        logger.warning("No fixtures endpoint available for managers, returning empty list")
        return []

    def get_results(self) -> list[Event]:
        """Fetch all results for this manager."""
        from .event import Event
        parsed_events = []
        for page in range(10):
            events_response = self._provider.get_manager_results(self.id, page=page)
            parsed_events.extend(events_response.events)
            if not events_response.hasNextPage:
                break
        return [Event(e, self._provider) for e in parsed_events]

    def get_events(self, *, max_events: Optional[int] = None, before: Optional[date | datetime] = None, after: Optional[date | datetime] = None) -> list[Event]:
        """Fetch events for this manager, optionally filtered by date range and/or max number of events."""
        events = self.get_results()
        if before is not None:
            events = [e for e in events if e.start < before]
            if max_events is not None:
                events = events[-max_events:]
        if after is not None:
            events = [e for e in events if e.start > after]
            if max_events is not None:
                events = events[:max_events]
        events.sort(key=lambda e: e.start)
        return events

    def _full_load(self) -> None:
        """TODO"""
        if self._full_loaded:
            return
        try:
            self._data = replace(self._data, **vars(self._provider.get_manager(self.id)))
            assert isinstance(self._data, ParsedManager)
            self._full_loaded = True
            self._clear_cache()
        except Exception:
            logger.exception(f"Failed to fully load manager with id {self.id}.")

    def _clear_cache(self) -> None:
        """Clear cached properties."""
        self.__dict__.pop("sport", None)
        self.__dict__.pop("country", None)
        self.__dict__.pop("team", None)
        self.__dict__.pop("teams", None)
        self.__dict__.pop("performances", None)
