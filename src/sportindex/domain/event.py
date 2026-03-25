from __future__ import annotations

from functools import cached_property
from dataclasses import dataclass
from datetime import datetime, date
from typing import TYPE_CHECKING, Optional, Literal

from . import logger
from .base import IdentifiableEntity, EntityCollection
from .core import Sport
from .competition import Season
from .utils import merge_dataclasses
from sportindex.provider.parsed import ParsedEvent, ParsedStage
from sportindex.exceptions import ProviderNotFoundError, FetchError, EntityNotFoundError, DomainError

if TYPE_CHECKING:
    from .channel import EventChannels
    from .competition import Competition
    from .competitor import Competitor
    from .components import (
        MatchCompetitors, MatchScore,
        MatchLineups, MatchPeriod,
        EventRound, MatchMomentumPoint,
        PeriodStats, Incident
    )
    from .leaderboard import Standings
    from .referee import Referee
    from .venue import Venue
    from sportindex.provider.parsed import SofascoreProvider


# ====== Event entity =====

class Event(IdentifiableEntity[ParsedEvent | ParsedStage]):
    """An event in a sport, such as a football match, tennis match, or motorsport race.

    Provides access to event metadata, competitors, scores, lineups, incidents, statistics, and associated entities
    like venue, referee, season, and competition. Supports both match- and race-specific properties.

    Attributes:
        id (int): Unique event ID.
        name (str): Event name.
        slug (str): URL-friendly identifier.
        start (datetime): Start time of the event.
        end (datetime | None): End time, if available.
        kind (Literal["match", "race"]): Type of event.
        round (EventRound | None): Event round, if applicable.
        sport (Sport): Sport associated with this event.
        season (Season): Season this event belongs to.
        competition (Competition): Competition this event belongs to.
        referee (Referee | None): Referee for the event, if available.
        venue (Venue | None): Venue where the event takes place.
        channels (EventChannels): TV or streaming channels broadcasting the event.

    Match-specific attributes:
        competitors (MatchCompetitors | None): Competitors in the event.
        score (MatchScore | None): Score of the match.
        periods (list[MatchPeriod] | None): Periods of the match.
        lineups (MatchLineups | None): Player lineups.
        incidents (list[Incident] | None): Notable incidents.
        statistics (list[PeriodStats] | None): Event statistics.
        momentum_graph (list[MatchMomentumPoint] | None): Momentum graph.
        h2h (EventCollection | None): Head-to-head history.

    Race-specific attributes:
        substages (EventCollection | None): Substages of the race.
        standings (EntityCollection[Standings] | None): Standings of competitors and teams.

    Post-event attributes:
        winner (Competitor | None): Winner of the event.

    Methods:
        from_id(event_id: int, provider) -> Event: Fetch an event by its unique ID.
        _full_load() -> None: Lazy-load full event details from the provider.
    """
    _REPR_FIELDS = ("id", "name", "slug", "start", "kind", "end", "round", "competitors")
    _TYPE_MAP = {ParsedEvent: 1, ParsedStage: 2}

    def __init__(self, data: ParsedEvent | ParsedStage, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, (ParsedEvent, ParsedStage)):
            raise TypeError("Event data must be either ParsedEvent or ParsedStage")

        self._full_loaded = False

    @property
    def id(self) -> int:
        """The unique ID of the event."""
        type_idx = self._TYPE_MAP[type(self._data)]
        return self.encode_id(self._data.id, type_idx)

    @property
    def name(self) -> str:
        """The name of the event."""
        return self._data.name if hasattr(self._data, "name") and self._data.name else self._data.slug.replace("-", " ").title()

    @property
    def slug(self) -> str:
        """The slug of the event (used in URLs)."""
        return self._data.slug

    @property
    def start(self) -> datetime:
        """The start time of the event."""
        return self._data.start

    @property
    def kind(self) -> Literal["match", "race"]:
        """The kind of the event (match or race)."""
        return "match" if isinstance(self._data, ParsedEvent) else "race"

    @property
    def end(self) -> Optional[datetime]:
        """The end time of the event, if available."""
        return self._data.end if hasattr(self._data, "end") else None

    @property
    def round(self) -> Optional[EventRound]:
        """The round of the event, if available."""
        from .components import EventRound
        return EventRound._from_parsed(self._data.roundInfo, provider=self._provider) if hasattr(self._data, "roundInfo") and self._data.roundInfo else None

    @property
    def sport(self) -> Sport:
        """The sport this event belongs to."""
        return self.season.sport

    @cached_property
    def season(self) -> Season:
        """The season this event belongs to."""
        from sportindex.provider.parsed import ParsedEvent, ParsedStage
        if isinstance(self._data, ParsedEvent):
            return Season(self._data.season, self._provider, uniqueTournament=self._data.tournament.uniqueTournament)
        elif isinstance(self._data, ParsedStage):
            parent_stage_id = self._data.stageParent.id
            parent_stage = self._provider.get_stage(parent_stage_id)
            return Season(parent_stage, self._provider)
        else:
            raise TypeError("Event data must be either ParsedEvent or ParsedStage to determine season")

    @property
    def competition(self) -> Competition:
        """The competition this event belongs to."""
        return self.season.competition

    @cached_property
    def referee(self) -> Optional[Referee]:
        """The referee for this event, if available."""
        from .referee import Referee
        if isinstance(self._data, ParsedEvent) and self._data.referee:
            return Referee(self._data.referee, self._provider)

    @cached_property
    def venue(self) -> Optional[Venue]:
        """The venue where this event takes place, if available."""
        from .venue import Venue
        if isinstance(self._data, ParsedEvent) and self._data.venue:
            return Venue(self._data.venue, self._provider)
        elif isinstance(self._data, ParsedStage):
            return Venue(self._data, self._provider)

    @property
    def channels(self) -> EventChannels:
        """Get the channels broadcasting this event, if match and available."""
        from .channel import EventChannels
        if isinstance(self._data, ParsedEvent):
            return EventChannels(self._provider.get_event_channels(self._data.id), self._provider)
        elif isinstance(self._data, ParsedStage):
            return EventChannels(self._provider.get_stage_channels(self._data.id), self._provider)


    # Match specific properties

    @cached_property
    def competitors(self) -> Optional[MatchCompetitors]:
        """The competitors in this event, if match and available."""
        if isinstance(self._data, ParsedEvent):
            from .competitor import Competitor
            from .components import MatchCompetitors
            return MatchCompetitors(
                home=Competitor(self._data.home.team, self._provider),
                away=Competitor(self._data.away.team, self._provider)
            )
        return None

    @property
    def score(self) -> Optional[MatchScore]:
        """The score for this event, if match and available."""
        if isinstance(self._data, ParsedEvent):
            return MatchScore(
                home=self._data.home.score,
                away=self._data.away.score
            )
        return None

    @property
    def periods(self) -> Optional[list[MatchPeriod]]:
        """The periods for this event, if match and available."""
        if isinstance(self._data, ParsedEvent):
            return [MatchPeriod._from_parsed(p) for p in self._data.parsedPeriods.periods]
        return None

    @cached_property
    def lineups(self) -> Optional[MatchLineups]:
        """The lineups for this event, if match and available."""
        if isinstance(self._data, ParsedEvent):
            try:
                from .components import MatchLineups, TeamLineup
                parsed_lineups = self._provider.get_event_lineups(self._data.id)
                if not parsed_lineups or not parsed_lineups.home or not parsed_lineups.away:
                    logger.debug(f"Lineups not found for event {self.id}.")
                    return None
                return MatchLineups(
                    home=TeamLineup._from_parsed(parsed_lineups.home, provider=self._provider),
                    away=TeamLineup._from_parsed(parsed_lineups.away, provider=self._provider)
                )
            except ProviderNotFoundError:
                logger.debug(f"Lineups not found for event {self.id}.")
                return None
        return None

    @property
    def incidents(self) -> Optional[list[Incident]]:
        """The incidents for this event, if match and available."""
        if isinstance(self._data, ParsedEvent):
            try:
                from .components import Incident
                parsed_incidents = self._provider.get_event_incidents(self._data.id)
                return [Incident._from_parsed(inc, provider=self._provider) for inc in parsed_incidents]
            except ProviderNotFoundError:
                logger.debug(f"Incidents not found for event {self.id}.")
                return None
        return None

    @cached_property
    def statistics(self) -> Optional[list[PeriodStats]]:
        """The statistics for this event, if match and available."""
        if isinstance(self._data, ParsedEvent):
            try:
                from .components import PeriodStats
                parsed_stats_response = self._provider.get_event_statistics(self._data.id)
                return [PeriodStats._from_parsed(s) for s in parsed_stats_response.statistics]
            except ProviderNotFoundError:
                logger.debug(f"Statistics not found for event {self.id}.")
                return None
        return None

    @property
    def momentum_graph(self) -> Optional[list[MatchMomentumPoint]]:
        """The momentum graph for this event, if match and available."""
        if isinstance(self._data, ParsedEvent):
            try:
                graph = self._provider.get_event_graph(self._data.id)
                if graph and graph.graphPoints:
                    from .components import MatchMomentumPoint
                    return [MatchMomentumPoint._from_parsed(p) for p in graph.graphPoints]
            except ProviderNotFoundError:
                logger.debug(f"Momentum graph not found for event {self.id}.")
                return None
        return None

    @cached_property
    def h2h(self) -> Optional[EventCollection]:
        """Head-to-head history for the competitors in this event, if match and available."""
        if isinstance(self._data, ParsedEvent):
            try:
                return EventCollection([Event(e, self._provider) for e in self._provider.get_h2h_history(self._data.customId).events])
            except ProviderNotFoundError:
                logger.debug(f"H2H history not found for event {self.id}.")
                return None
        return None


    # Race specific properties

    @cached_property
    def substages(self) -> Optional[EventCollection]:
        """The substages for this event, if race and available."""
        if isinstance(self._data, ParsedStage):
            try:
                return EventCollection([Event(s, self._provider) for s in self._provider.get_stage_substages(self._data.id)])
            except ProviderNotFoundError:
                logger.debug(f"Substages not found for event {self.id}.")
                return None
        return None

    @property
    def standings(self) -> Optional[EntityCollection[Standings]]:
        """The standings for this event, if race and available."""
        if isinstance(self._data, ParsedStage):
            try:
                competitors_standings = self._provider.get_stage_standings_competitors(self._data.id)
            except ProviderNotFoundError as e:
                logger.debug(f"Failed to fetch competitors standings for event {self.id}: {e}")
                competitors_standings = []
            try:
                teams_standings = self._provider.get_stage_standings_teams(self._data.id)
            except ProviderNotFoundError as e:
                logger.debug(f"Failed to fetch teams standings for event {self.id}: {e}")
                teams_standings = []
            return EntityCollection([
                Standings(competitors_standings, self._provider, name=f"Competitors {self.name}", kind="competitors"),
                Standings(teams_standings, self._provider, name=f"Teams {self.name}", kind="teams")
            ])
        return None


    # Post event properties (available for both matches and races)

    @cached_property
    def winner(self) -> Optional[Competitor]:
        """The winner of this event, if available."""
        if isinstance(self._data, ParsedEvent):
            winner_code = self._data.winnerCode
            if winner_code == 1:
                return Competitor(self._data.home.team, self._provider)
            elif winner_code == 2:
                return Competitor(self._data.away.team, self._provider)
        elif isinstance(self._data, ParsedStage):
            if self._data.winner:
                return Competitor(self._data.winner, self._provider)
        return None

    def _full_load(self) -> None:
        """
        Lazy-loads the complete event from the provider.
        Called automatically when accessing properties that require full details
        missing from the initial lightweight API response.
        """
        if self._full_loaded:
            return
        try:
            if isinstance(self._data, ParsedEvent):
                self._data = merge_dataclasses(self._data, self._provider.get_event(self._data.id))
            elif isinstance(self._data, ParsedStage):
                self._data = merge_dataclasses(self._data, self._provider.get_stage_details(self._data.id))
            if not isinstance(self._data, (ParsedEvent, ParsedStage)):
                raise TypeError("Event data must be either ParsedEvent or ParsedStage")
            self._full_loaded = True
            self._clear_cache()
        except ProviderNotFoundError:
            logger.debug(f"Event with id {self._data.id} not found during full load.")
            self._full_loaded = True
            self._clear_cache()
        except FetchError as e:
            logger.debug(f"Network error while fully loading event with id {self._data.id}: {e}")
            self._full_loaded = True
            self._clear_cache()

    def _clear_cache(self) -> None:
        """Clear cached properties."""
        self.__dict__.pop("season", None)
        self.__dict__.pop("venue", None)
        self.__dict__.pop("competitors", None)
        self.__dict__.pop("score", None)
        self.__dict__.pop("lineups", None)
        self.__dict__.pop("h2h", None)
        self.__dict__.pop("substages", None)

    @classmethod
    def from_id(cls, event_id: int, provider: SofascoreProvider) -> Event:
        """Fetch an event by its ID."""
        raw_id, type_idx = cls.decode_id(event_id)
        type_map_reverse = {v: k for k, v in cls._TYPE_MAP.items()}

        if type_idx not in type_map_reverse:
            raise ValueError(f"Invalid event ID {event_id}: unknown type index {type_idx}")

        data_cls = type_map_reverse[type_idx]
        try:
            if data_cls == ParsedEvent:
                parsed_data = provider.get_event(raw_id)
            elif data_cls == ParsedStage:
                parsed_data = provider.get_stage(raw_id)
            else:
                raise TypeError(f"Unsupported event type index {type_idx} in ID {event_id}")
        except ProviderNotFoundError as e:
            raise EntityNotFoundError(f"Event with id {event_id} not found") from e
        except FetchError as e:
            raise DomainError(f"Network error while fetching event {event_id}") from e

        return cls(parsed_data, provider)


# ===== Event Collection =====

class EventCollection(EntityCollection[Event]):
    """A specialized collection for handling lists of events with common filtering and sorting needs."""

    def filter_by_date(self, *, before: Optional[date | datetime] = None, after: Optional[date | datetime] = None) -> EventCollection:
        """Return a new EventCollection filtered by date."""
        results = self._entities

        def to_dt(val: date | datetime) -> datetime:
            if isinstance(val, datetime): return val
            return datetime.combine(val, datetime.min.time())

        if before is not None:
            before_dt = to_dt(before)
            results = [e for e in results if e.start < before_dt]
        if after is not None:
            after_dt = to_dt(after)
            results = [e for e in results if e.start > after_dt]

        return self.__class__(results)

    def filter_by_competitors(self, competitor_ids: list[int]) -> EventCollection:
        """Return a new EventCollection filtered by competitor IDs."""
        results = []
        for event in self._entities:
            if event.competitors:
                if (event.competitors.home.id in competitor_ids) or (event.competitors.away.id in competitor_ids):
                    results.append(event)
        return self.__class__(results)

    def sort_by_date(self, ascending: bool = True) -> EventCollection:
        """Return a new EventCollection sorted by date."""
        return self.__class__(sorted(self._entities, key=lambda e: e.start, reverse=not ascending))
