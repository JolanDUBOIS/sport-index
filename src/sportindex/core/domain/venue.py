from __future__ import annotations

from functools import cached_property
from dataclasses import replace
from datetime import datetime, date
from typing import TYPE_CHECKING, Optional

from . import logger
from .base import BaseEntity
from sportindex.core.provider.parsed import ParsedVenue, ParsedStage

if TYPE_CHECKING:
    from .core import Country
    from .event import Event
    from .competitor import Competitor
    from sportindex.core.provider.parsed import ParsedSofascoreProvider


class Venue(BaseEntity[ParsedVenue]):
    """A venue, e.g. a stadium, a tennis court, a race track, etc."""
    REPR_FIELDS = ("id", "name")

    def __init__(self, data: ParsedVenue | ParsedStage, provider: ParsedSofascoreProvider | None = None, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, (ParsedVenue, ParsedStage)):
            raise ValueError("Venue data must be either ParsedVenue or ParsedStage")

    @property
    def name(self) -> str:
        """The name of the venue."""
        if isinstance(self._data, ParsedVenue):
            return self._data.name or (self._data.stadium.name if self._data.stadium else "")
        elif isinstance(self._data, ParsedStage):
            return self._data.info.circuit if self._data.info else ""

    @property
    def city(self) -> Optional[str]:
        """The city where the venue is located."""
        self._full_load()
        if isinstance(self._data, ParsedVenue):
            return self._data.city
        elif isinstance(self._data, ParsedStage):
            return self._data.info.circuitCity if self._data.info else None

    @property
    def capacity(self) -> Optional[int]:
        """The capacity of the venue, if available."""
        if isinstance(self._data, ParsedVenue):
            self._full_load()
            return self._data.capacity or (self._data.stadium.capacity if self._data.stadium else None)
        elif isinstance(self._data, ParsedStage):
            return None

    @cached_property
    def country(self) -> Optional[Country]:
        """The country where the venue is located, if available."""
        self._full_load()
        if isinstance(self._data, ParsedVenue):
            return Country(self._data.country, self._provider)
        elif isinstance(self._data, ParsedStage):
            return Country.from_name(self._data.info.circuitCountry) if self._data.info and self._data.info.circuitCountry else None

    @cached_property
    def teams(self) -> list[Competitor]:
        self._full_load()
        from .competitor import Competitor
        if isinstance(self._data, ParsedVenue):
            return [
                Competitor(t, self._provider)
                for t in self._data.mainTeams
            ]
        elif isinstance(self._data, ParsedStage):
            logger.warning("Teams for stages are not available in the current provider implementation, returning empty list")
            return []

    def get_fixtures(self) -> list[Event]:
        """Fetch all fixtures for this venue."""
        from .event import Event
        parsed_events = []
        for page in range(10):
            events_response = self._provider.get_venue_fixtures(self.id, page=page)
            parsed_events.extend(events_response.events)
            if not events_response.hasNextPage:
                break
        return [Event(e, self._provider) for e in parsed_events]

    def get_results(self) -> list[Event]:
        """Fetch all results for this venue."""
        from .event import Event
        parsed_events = []
        for page in range(10):
            events_response = self._provider.get_venue_results(self.id, page=page)
            parsed_events.extend(events_response.events)
            if not events_response.hasNextPage:
                break
        return [Event(e, self._provider) for e in parsed_events]

    def get_events(self, *, max_events: Optional[int] = None, before: Optional[date | datetime] = None, after: Optional[date | datetime] = None) -> list[Event]:
        """Fetch events for this venue, optionally filtered by date range and/or max number of events."""
        events = self.get_results() + self.get_fixtures()
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
            self._data = replace(self._data, **vars(self._provider.get_venue(self.id)))
            assert isinstance(self._data, ParsedVenue)
            self._full_loaded = True
            self._clear_cache()
        except Exception:
            logger.exception(f"Failed to fully load venue with id {self.id}.")

    def _clear_cache(self) -> None:
        """Clear cached properties."""
        self.__dict__.pop("country", None)
        self.__dict__.pop("teams", None)
