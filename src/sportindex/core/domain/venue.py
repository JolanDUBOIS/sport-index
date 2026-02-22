"""
Venue domain entity.

Represents a physical location (stadium, arena, circuit) where events
take place.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Optional, TYPE_CHECKING

from .base import BaseEntity, _normalize_dt
from .values import Coordinates, _coordinates_from_raw

if TYPE_CHECKING:
    from .core import Country
    from .event import Event
    from .participant import Competitor

logger = logging.getLogger(__name__)


class Venue(BaseEntity):
    """A physical venue (stadium, arena, circuit)."""

    def __init__(
        self,
        *,
        id: int,
        name: str,
        slug: str = "",
        city: Optional[str] = None,
        country: Optional[Country] = None,
        coordinates: Optional[Coordinates] = None,
        capacity: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.id = id
        self.name = name
        self.slug = slug
        self.city = city
        self.country = country
        self.coordinates = coordinates
        self.capacity = capacity

        self._teams: Optional[list[Competitor]] = None

    # -- Constructor --------------------------------------------------- #

    @classmethod
    def _from_raw(cls, raw: dict | None) -> Optional[Venue]:
        """Build from a RawVenue dict. Returns None if raw is empty."""
        if not raw or "id" not in raw:
            return None

        from .core import Country

        # Capacity can be on the venue directly, or nested under stadium
        capacity = raw.get("capacity")
        if capacity is None:
            stadium = raw.get("stadium")
            if isinstance(stadium, dict):
                capacity = stadium.get("capacity")

        return cls(
            id=raw["id"],
            name=raw.get("name", ""),
            slug=raw.get("slug", ""),
            city=raw.get("city"),
            country=Country._from_raw(raw.get("country")),
            coordinates=_coordinates_from_raw(raw.get("coordinates")),
            capacity=capacity,
        )

    # -- Lazy properties ----------------------------------------------- #

    @property
    def teams(self) -> list[Competitor]:
        """Teams that play at this venue (lazy)."""
        if self._teams is not None:
            return self._teams

        from .participant import Competitor

        self._load_full()
        raw_teams = self._raw.get("mainTeams", [])
        self._teams = [
            Competitor._from_raw_team(t)
            for t in raw_teams
        ]
        return self._teams

    # -- Event fetching ------------------------------------------------ #

    def events(
        self,
        *,
        max_events: int | None = None,
        before: date | datetime | None = None,
        after: date | datetime | None = None,
    ) -> list[Event]:
        """Fetch all events at this venue (merges results + fixtures).

        Args:
            max_events: Stop after collecting this many events.
            before: Only events starting strictly before this date/datetime.
            after:  Only events starting strictly after this date/datetime.
        """
        before_dt = _normalize_dt(before)
        after_dt = _normalize_dt(after)
        vid = str(self.id)

        logger.debug("Fetching all events for venue '%s' (id=%s)", self.name, self.id)
        past = self._fetch_event_pages(
            lambda p: self._provider.get_venue_results(vid, page=p),
            before=before_dt,
            after=after_dt,
            ascending=False,
            first_page=1,
        )
        future = self._fetch_event_pages(
            lambda p: self._provider.get_venue_fixtures(vid, page=p),
            before=before_dt,
            after=after_dt,
            ascending=True,
            first_page=1,
        )
        all_events = past + future
        all_events.sort(key=lambda e: e.start or datetime.min)
        if max_events is not None:
            all_events = all_events[:max_events]
        return all_events

    def fixtures(
        self,
        *,
        max_events: int | None = None,
        before: date | datetime | None = None,
        after: date | datetime | None = None,
    ) -> list[Event]:
        """Fetch upcoming fixtures at this venue.

        Defaults to events starting after *now*.

        Args:
            max_events: Stop after collecting this many events.
            before: Only events starting strictly before this date/datetime.
            after:  Only events starting strictly after this date/datetime.
                    Defaults to now.
        """
        if after is None:
            after = datetime.now()
        vid = str(self.id)

        logger.debug("Fetching fixtures for venue '%s' (id=%s)", self.name, self.id)
        return self._fetch_event_pages(
            lambda p: self._provider.get_venue_fixtures(vid, page=p),
            max_events=max_events,
            before=_normalize_dt(before),
            after=_normalize_dt(after),
            ascending=True,
            first_page=1,
        )

    def results(
        self,
        *,
        max_events: int | None = None,
        before: date | datetime | None = None,
        after: date | datetime | None = None,
    ) -> list[Event]:
        """Fetch results at this venue.

        Defaults to events starting before *now*.

        Args:
            max_events: Stop after collecting this many events.
            before: Only events starting strictly before this date/datetime.
                    Defaults to now.
            after:  Only events starting strictly after this date/datetime.
        """
        if before is None:
            before = datetime.now()
        vid = str(self.id)

        logger.debug("Fetching results for venue '%s' (id=%s)", self.name, self.id)
        return self._fetch_event_pages(
            lambda p: self._provider.get_venue_results(vid, page=p),
            max_events=max_events,
            before=_normalize_dt(before),
            after=_normalize_dt(after),
            ascending=False,
            first_page=1,
        )

    # -- Internal ------------------------------------------------------ #

    def _load_full(self) -> None:
        if self._full_loaded:
            return
        logger.debug("Loading full data for venue '%s' (id=%s)", self.name, self.id)
        self._raw.update(self._provider.get_venue(str(self.id)))
        self._full_loaded = True


