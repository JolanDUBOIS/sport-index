"""
Season domain entity.

A Season represents a specific year/edition of a Competition.
It can come from a RawSeason (tournament-based sports) or a
RawStage (motorsport / cycling season-stage).
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Optional, Literal, TYPE_CHECKING

from .base import BaseEntity, _normalize_dt
from ..provider.parsers import timestamp_to_dt

if TYPE_CHECKING:
    from .competition import Competition
    from .event import Event
    from .leaderboard import Standings

logger = logging.getLogger(__name__)


class Season(BaseEntity):
    """A season within a competition (e.g. '2024/25 Premier League')."""

    def __init__(
        self,
        *,
        id: int,
        name: str,
        year: str,
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> None:
        super().__init__()
        self.id = id
        self.name = name
        self.year = year
        self.start = start
        self.end = end

        self._competition: Optional[Competition] = None
        self._source: Optional[Literal["tournament", "stage"]] = None
        self._standings: Optional[list[Standings]] = None

    # -- Constructors -------------------------------------------------- #

    @classmethod
    def _from_raw_season_tournament(
        cls,
        raw: dict,
        *,
        competition: Optional[Competition] = None,
    ) -> Season:
        """Build from a RawSeason dict (tournament-based sports)."""
        start = timestamp_to_dt(raw.get("startDateTimestamp"), kind="date")
        season = cls(
            id=raw.get("id", 0),
            name=raw.get("name", ""),
            year=raw.get("year", raw.get("name", "")),
            start=start
        )
        season._competition = competition
        season._raw = raw
        season._source = "tournament"
        return season

    @classmethod
    def _from_raw_season_stage(
        cls,
        raw: dict,
        *,
        competition: Optional[Competition] = None,
    ) -> Season:
        """Build from a RawStage dict (motorsport season-stage)."""
        start = timestamp_to_dt(raw.get("startDateTimestamp"), kind="date")
        end = timestamp_to_dt(raw.get("endDateTimestamp"), kind="date")
        season = cls(
            id=raw.get("id", 0),
            name=raw.get("name", ""),
            year=raw.get("year", raw.get("name", "")),
            start=start,
            end=end
        )
        season._competition = competition
        season._raw = raw
        season._source = "stage"
        return season

    # -- Properties ---------------------------------------------------- #

    @property
    def competition(self) -> Optional[Competition]:
        return self._competition

    @property
    def standings(self) -> list[Standings]:
        """Fetch standings for this season (lazy).

        Tournament seasons return standings for each view (total, home, away).
        Stage seasons return standings for each view (competitors, teams).
        """
        if self._standings is not None:
            return self._standings

        from .leaderboard import Standings

        if self._competition is None:
            logger.warning("Cannot fetch standings: no parent competition set on season '%s'", self.name)
            self._standings = []
            return self._standings

        if self._source == "stage":
            stage_id = str(self.id)
            logger.debug("Fetching stage standings for season '%s' (id=%s)", self.name, self.id)

            raw_constructors = self._provider.get_stage_standings_competitors(stage_id)
            raw_drivers = self._provider.get_stage_standings_teams(stage_id)

            standings_list: list[Standings] = []
            if raw_constructors:
                constructors = Standings(
                    id=self.id,
                    name="Constructors",
                )
                constructors._view = "competitors"
                constructors._basis = "racing"
                constructors._raw = {"rows": raw_constructors}
                standings_list.append(constructors)

            if raw_drivers:
                drivers = Standings(
                    id=self.id,
                    name="Drivers",
                )
                drivers._view = "teams"
                drivers._basis = "racing"
                drivers._raw = {"rows": raw_drivers}
                standings_list.append(drivers)

            self._standings = standings_list
            return self._standings

        else:
            comp_id = str(self._competition.id)
            season_id = str(self.id)
            logger.debug("Fetching standings for season '%s' (id=%s)", self.name, self.id)

            all_standings: list[Standings] = []
            for view in ("total", "home", "away"):
                raw_list = self._provider.get_unique_tournament_standings(
                    comp_id, season_id, view=view,
                )
                for raw_s in raw_list:
                    s = Standings._from_raw(raw_s)
                    s._view = view
                    all_standings.append(s)

            self._standings = all_standings
            return self._standings

    # -- Event fetching ------------------------------------------------ #

    def _stage_events(
        self,
        *,
        before: datetime | None = None,
        after: datetime | None = None,
        max_events: int | None = None,
    ) -> list[Event]:
        """Fetch substages for a stage season and return them as Events.

        Single API call (no pagination).  Filtering is applied on
        ``startDateTimestamp`` after fetching all substages.
        """
        from .event import Event

        logger.debug("Fetching substages for stage season '%s' (id=%s)", self.name, self.id)
        raw_substages = self._provider.get_stage_substages(str(self.id))

        events: list[Event] = []
        for raw in raw_substages:
            ev = Event._from_raw_stage(raw)
            if ev.start is not None:
                if before is not None and ev.start >= before:
                    continue
                if after is not None and ev.start <= after:
                    continue
            events.append(ev)

        events.sort(key=lambda e: e.start or datetime.min)
        if max_events is not None:
            events = events[:max_events]
        return events

    def events(
        self,
        *,
        max_events: int | None = None,
        before: date | datetime | None = None,
        after: date | datetime | None = None,
    ) -> list[Event]:
        """Fetch all events for this season.

        For tournament seasons, merges results and fixtures (two paginated
        endpoint chains).  For stage seasons, fetches substages in a
        single call.

        Args:
            max_events: Stop after collecting this many events.
            before: Only events starting strictly before this date/datetime.
            after:  Only events starting strictly after this date/datetime.
        """
        before_dt = _normalize_dt(before)
        after_dt = _normalize_dt(after)

        if self._source == "stage":
            return self._stage_events(before=before_dt, after=after_dt, max_events=max_events)

        if self._competition is None:
            logger.warning("Cannot fetch events: no parent competition for season '%s'", self.name)
            return []

        comp_id = str(self._competition.id)
        season_id = str(self.id)

        logger.debug("Fetching all events for season '%s' (id=%s)", self.name, self.id)
        past = self._fetch_event_pages(
            lambda p: self._provider.get_unique_tournament_results(comp_id, season_id, page=p),
            before=before_dt,
            after=after_dt,
            ascending=False,
        )
        future = self._fetch_event_pages(
            lambda p: self._provider.get_unique_tournament_fixtures(comp_id, season_id, page=p),
            before=before_dt,
            after=after_dt,
            ascending=True,
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
        """Fetch upcoming fixtures for this season.

        Defaults to events starting after *now*.  Uses the dedicated
        fixtures endpoint for tournament seasons.  For stage seasons,
        filters substages by start date.

        Args:
            max_events: Stop after collecting this many events.
            before: Only events starting strictly before this date/datetime.
            after:  Only events starting strictly after this date/datetime.
                    Defaults to now.
        """
        if after is None:
            after = datetime.now()

        before_dt = _normalize_dt(before)
        after_dt = _normalize_dt(after)

        if self._source == "stage":
            return self._stage_events(before=before_dt, after=after_dt, max_events=max_events)

        if self._competition is None:
            logger.warning("Cannot fetch fixtures: no parent competition for season '%s'", self.name)
            return []

        comp_id = str(self._competition.id)
        season_id = str(self.id)

        logger.debug("Fetching fixtures for season '%s' (id=%s)", self.name, self.id)
        return self._fetch_event_pages(
            lambda p: self._provider.get_unique_tournament_fixtures(comp_id, season_id, page=p),
            max_events=max_events,
            before=before_dt,
            after=after_dt,
            ascending=True,
        )

    def results(
        self,
        *,
        max_events: int | None = None,
        before: date | datetime | None = None,
        after: date | datetime | None = None,
    ) -> list[Event]:
        """Fetch results for this season.

        Defaults to events starting before *now*.  Uses the dedicated
        results endpoint for tournament seasons.  For stage seasons,
        filters substages by start date.

        Args:
            max_events: Stop after collecting this many events.
            before: Only events starting strictly before this date/datetime.
                    Defaults to now.
            after:  Only events starting strictly after this date/datetime.
        """
        if before is None:
            before = datetime.now()

        before_dt = _normalize_dt(before)
        after_dt = _normalize_dt(after)

        if self._source == "stage":
            return self._stage_events(before=before_dt, after=after_dt, max_events=max_events)

        if self._competition is None:
            logger.warning("Cannot fetch results: no parent competition for season '%s'", self.name)
            return []

        comp_id = str(self._competition.id)
        season_id = str(self.id)

        logger.debug("Fetching results for season '%s' (id=%s)", self.name, self.id)
        return self._fetch_event_pages(
            lambda p: self._provider.get_unique_tournament_results(comp_id, season_id, page=p),
            max_events=max_events,
            before=before_dt,
            after=after_dt,
            ascending=False,
        )
