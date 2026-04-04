from __future__ import annotations

from abc import abstractmethod
from functools import cached_property
from pydantic import BaseModel
from datetime import datetime, date
from typing import (
    TYPE_CHECKING, Optional, TypeVar,
    TypeAlias, Generic, Callable,
    Literal, overload
)

from . import logger
from .base import IdentifiableEntity, EntityCollection
from .core import Sport
from .types import EventFormat
from .utils import merge_pydantic_models
from sportindex.exceptions import ProviderNotFoundError, FetchError, EntityNotFoundError, DomainError
from sportindex.provider.models import _EventData, _StageData, StageTier

if TYPE_CHECKING:
    from .channel import EventChannels
    from .competition import Competition
    from .competitor import Competitor
    from .incident import Incident
    from .leaderboard import Standings
    from .referee import Referee
    from .season import Season
    from .venue import Venue
    from sportindex.provider import SofascoreProvider
    from sportindex.provider.models import (
        Round, Score, MatchPeriod, PeriodStats,
        _LineupsResponse, MomentumPoint, EventStatus,
        _EventsResponse
    )


# ===== Components =====

class MatchCompetitors(BaseModel):
    """Represents the two competitors in a match."""
    home: Competitor
    away: Competitor


class MatchLineups(BaseModel):
    """Represents the lineups of both teams for a match."""
    home: list[Competitor]
    away: list[Competitor]

    @classmethod
    def _from_base_schema(cls, lineup_response: _LineupsResponse, provider: SofascoreProvider) -> MatchLineups:
        """Create MatchLineups from a _LineupsResponse."""
        if not lineup_response or not lineup_response.home or not lineup_response.away:
            logger.debug(f"Lineups response is incomplete for event. Response: {lineup_response}")
            raise ProviderNotFoundError("Lineups data is incomplete or missing")
        return cls(
            home=[Competitor(p, provider) for p in lineup_response.home.players],
            away=[Competitor(p, provider) for p in lineup_response.away.players]
        )


# ===== Event entity =====

class Event(IdentifiableEntity):
    """An event in a sport, such as a football match, tennis match, or motorsport race.

    Provides access to event metadata, competitors, scores, lineups, incidents, statistics, and associated entities
    like venue, referee, season, and competition. Supports both match- and race-specific properties.

    Attributes:
        id (int): Unique event ID, encoded from source ID and type.
        name (str): Event name.
        slug (str): URL-friendly identifier.
        start (datetime): Start time of the event.
        status (EventStatus | None): Current status of the event, if available.
        sport (Sport): Sport associated with this event.

    Abstract properties:
        format (Literal["match", "stage"]): The format of the event, either 'match' or 'stage'.
        competition (Competition | None): Competition this event belongs to.
        season (Season): Season this event belongs to.
        venue (Venue | None): Venue where the event takes place.
        channels (EventChannels): TV or streaming channels broadcasting the event.
        winner (Competitor | None): Winner of the event.

    Methods:
        from_id(event_id: int, provider) -> Event: Fetch an event by its unique ID.
    """
    _data: _EventData | _StageData
    _REPR_FIELDS = ("id", "name", "slug", "start")
    _TYPE_MAP = {_EventData: 1, _StageData: 2}
    _DOMAIN_MAP: dict[int, type[Event]] = {}

    def __new__(cls, data: _EventData | _StageData, provider: SofascoreProvider, **kwargs):
        """Create the correct subclass based on the data type."""
        if cls is Event:
            if isinstance(data, _EventData):
                return super().__new__(MatchEvent)
            elif isinstance(data, _StageData):
                return super().__new__(StageEvent)
        return super().__new__(cls)

    def __init__(self, data: _EventData | _StageData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, (_EventData, _StageData)):
            raise TypeError(f"Event data must be either _EventData or _StageData, got {type(data)}")

        self._full_loaded = False

    @property
    def id(self) -> int:
        """The unique ID of the event."""
        type_idx = self._TYPE_MAP[type(self._data)]
        return self.encode_id(self._data.id, type_idx)

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the event."""
        raise NotImplementedError("Property name must be implemented in subclasses")

    @property
    def slug(self) -> str:
        """The slug of the event (used in URLs)."""
        return self._data.slug

    @property
    def start(self) -> datetime:
        """The start time of the event."""
        return self._data.start

    @property
    def status(self) -> Optional[EventStatus]:
        """The status of the event, if available."""
        return self._data.status

    @property
    def sport(self) -> Sport:
        """The sport this event belongs to."""
        return self.season.sport

    @property
    @abstractmethod
    def format(self) -> EventFormat:
        """The format of the event, either 'match' or 'stage'."""
        raise NotImplementedError("Property format must be implemented in subclasses")

    @property
    @abstractmethod
    def competition(self) -> Optional[Competition]:
        """The competition this event belongs to, if available."""
        raise NotImplementedError("Property competition must be implemented in subclasses")

    @property
    @abstractmethod
    def season(self) -> Season:
        """The season this event belongs to."""
        raise NotImplementedError("Property season must be implemented in subclasses")

    @property
    @abstractmethod
    def venue(self) -> Optional[Venue]:
        """The venue where this event takes place, if available."""
        raise NotImplementedError("Property venue must be implemented in subclasses")

    @property
    @abstractmethod
    def channels(self) -> EventChannels:
        """Get the channels broadcasting this event."""
        raise NotImplementedError("Property channels must be implemented in subclasses")

    @property
    @abstractmethod
    def winner(self) -> Optional[Competitor]:
        """The winner of this event, if available."""
        raise NotImplementedError("Property winner must be implemented in subclasses")

    def _full_load(self) -> None:
        """
        Lazy-loads the complete event from the provider.
        Called automatically when accessing properties that require full details
        missing from the initial lightweight API response.
        """
        if self._full_loaded:
            return

        self._data = merge_pydantic_models(self._data, self._fetch_entity(self._data.id, self._provider, strict=False))

        self._full_loaded = True
        self._clear_cache()

    @classmethod
    def from_id(cls, event_id: int, provider: SofascoreProvider) -> Event:
        """Fetch an event by its ID."""
        raw_id, type_idx = cls.decode_id(event_id)

        if type_idx not in cls._DOMAIN_MAP:
            raise TypeError(f"Invalid event ID {event_id}: unknown type index {type_idx}")

        target_subclass = cls._DOMAIN_MAP[type_idx]
        entity_data = target_subclass._fetch_entity(raw_id, provider, strict=False)

        return cls(entity_data, provider)

    @overload
    @classmethod
    def _fetch_entity(cls, entity_id: int, provider: SofascoreProvider, strict: Literal[True] = True) -> _EventData | _StageData: ...

    @overload
    @classmethod
    def _fetch_entity(cls, entity_id: int, provider: SofascoreProvider, strict: Literal[False]) -> Optional[_EventData | _StageData]: ...

    @classmethod
    @abstractmethod
    def _fetch_entity(cls, entity_id: int, provider: SofascoreProvider, strict: bool = True) -> Optional[_EventData | _StageData]:
        """Fetch the complete event data from the provider by its raw ID."""
        raise NotImplementedError("Method _fetch_entity must be implemented in subclasses")


class MatchEvent(Event):
    """An event representing a match between two competitors, such as a football or tennis match.
    
    Provides access to match-specific properties like score, winner, periods, lineups, incidents, statistics, 
    and momentum graphs, extending the base event properties.

    Attributes:
        round (Round | None): The round of the match event.
        referee (Referee | None): The referee officiating the match.
        competitors (MatchCompetitors): The home and away competitors.
        score (Score | None): The current or final score.
        periods (list[MatchPeriod]): The periods of the match.
        lineups (MatchLineups | None): The starting lineups for both teams.
        incidents (list[Incident]): In-game incidents like cards or goals.
        statistics (list[PeriodStats]): Statistical data for the match periods.
        momentum_graph (list[MomentumPoint]): Data points representing match momentum.
        h2h (EventCollection): Head-to-head history between the two competitors.
    """
    _data: _EventData

    def __init__(self, data: _EventData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _EventData):
            raise TypeError(f"MatchEvent data must be _EventData, got {type(data)}")

    # Properties available before the match starts

    @property
    def name(self) -> str:
        """The name of the match event."""
        return self._data.slug.replace("-", " ").title()

    @property
    def round(self) -> Optional[Round]:
        """The round of the match event, if available."""
        return self._data.round

    @property
    def format(self) -> EventFormat:
        """The format of the event, either 'match' or 'stage'."""
        return "match"

    @property
    def competition(self) -> Optional[Competition]:
        """The competition this event belongs to, if available."""
        self._full_load()
        from .competition import Competition
        return Competition(self._data.tournament.unique_tournament, self._provider) if self._data.tournament and self._data.tournament.unique_tournament else None

    @cached_property
    def season(self) -> Season:
        """The season this event belongs to."""
        self._full_load()
        from .season import Season
        return Season(self._data.season, self._provider, uniqueTournament=self._data.tournament.unique_tournament)

    @cached_property
    def referee(self) -> Optional[Referee]:
        """The referee for this event, if available."""
        self._full_load()
        from .referee import Referee
        return Referee(self._data.referee, self._provider) if self._data.referee else None

    @cached_property
    def competitors(self) -> MatchCompetitors:
        """The competitors in this event."""
        from .competitor import Competitor
        return MatchCompetitors(
            home=Competitor(self._data.home.team, self._provider),
            away=Competitor(self._data.away.team, self._provider)
        )

    @cached_property
    def venue(self) -> Venue:
        """The venue where this event takes place."""
        self._full_load()
        from .venue import Venue
        return Venue(self._data.venue, self._provider)

    @cached_property
    def channels(self) -> EventChannels:
        from .channel import EventChannels
        return EventChannels(self._provider.get_event_channels(self._data.id), self._provider)

    # Properties available after the match starts or ends

    @property
    def score(self) -> Optional[Score]:
        """The score for this event, if available."""
        from sportindex.provider.models import Score
        return Score(
            home=self._data.home.score,
            away=self._data.away.score
        )

    @property
    def winner(self) -> Optional[Competitor]:
        """The winner of this event, if available."""
        self._full_load()
        winner_code = self._data.winner_code
        if winner_code == 1:
            return self.competitors.home
        elif winner_code == 2:
            return self.competitors.away
        return None

    @property
    def periods(self) -> list[MatchPeriod]:
        """The periods for this event, if available."""
        self._full_load()
        return self._data.periods.periods if self._data.periods else []

    @cached_property
    def lineups(self) -> Optional[MatchLineups]:
        """The lineups for this event, if available."""
        try:
            parsed_lineups = self._provider.get_event_lineups(self._data.id)
            return MatchLineups._from_base_schema(parsed_lineups, self._provider)
        except ProviderNotFoundError:
            logger.debug(f"Lineups not found for event {self.id}.")
            return None

    @property
    def incidents(self) -> list[Incident]:
        """
        The incidents for this event, if available.
        Not cached because it updates regularly during the match.
        """
        try:
            from .incident import to_domain_incident
            parsed_incidents = self._provider.get_event_incidents(self._data.id)
            return [to_domain_incident(inc, provider=self._provider) for inc in parsed_incidents]
        except ProviderNotFoundError:
            logger.debug(f"Incidents not found for event {self.id}.")
            return []

    @cached_property
    def statistics(self) -> list[PeriodStats]:
        """The statistics for this event, if available."""
        try:
            parsed_stats_response = self._provider.get_event_statistics(self._data.id)
            if parsed_stats_response:
                return parsed_stats_response.statistics
        except ProviderNotFoundError:
            logger.debug(f"Statistics not found for event {self.id}.")
            return []

    @property
    def momentum_graph(self) -> list[MomentumPoint]:
        """
        The momentum graph for this event, if available.
        Not cached because it updates every minute during the match.
        """
        try:
            graph = self._provider.get_event_graph(self._data.id)
            if graph:
                return graph.points
        except ProviderNotFoundError:
            logger.debug(f"Momentum graph not found for event {self.id}.")
            return []

    @cached_property
    def h2h(self) -> EventCollection:
        """Head-to-head history for the competitors in this event, if available."""
        try:
            return EventCollection([Event(e, self._provider) for e in self._provider.get_h2h_history(self._data.custom_id).events])
        except ProviderNotFoundError:
            logger.debug(f"H2H history not found for event {self.id}.")
            return EventCollection([])

    @overload
    @classmethod
    def _fetch_entity(cls, entity_id: int, provider: SofascoreProvider, strict: Literal[True] = True) -> _EventData: ...

    @overload
    @classmethod
    def _fetch_entity(cls, entity_id: int, provider: SofascoreProvider, strict: Literal[False]) -> Optional[_EventData]: ...

    @classmethod
    def _fetch_entity(cls, entity_id: int, provider: SofascoreProvider, strict: bool = True) -> Optional[_EventData]:
        """Fetch the complete event data from the provider by its raw ID."""
        try:
            return provider.get_event(entity_id)
        except ProviderNotFoundError:
            logger.debug(f"Event with id {entity_id} not found during fetch.")
            if strict:
                raise EntityNotFoundError(f"Event with id {entity_id} not found") from None
        except FetchError as e:
            logger.debug(f"Network error while fetching event with id {entity_id}: {e}")
            if strict:
                raise DomainError(f"Network error while fetching event with id {entity_id}") from e
        return None


class StageEvent(Event):
    """An event representing a specific stage, phase, or race within a competition.
    
    Provides access to stage-specific properties like tiers, parent-child relationships, 
    and team/competitor standings.

    Attributes:
        end (datetime | None): The scheduled end time of the stage.
        tier (StageTier): The categorization tier of the stage.
        parent (StageEvent | None): The overarching parent stage, if applicable.
        substages (EventCollection): Any child stages contained within this stage.
        standings (EntityCollection[Standings] | None): The rankings for competitors and teams.
    """
    _data: _StageData

    def __init__(self, data: _StageData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _StageData):
            raise TypeError(f"StageEvent data must be _StageData, got {type(data)}")
        if data.tier and data.tier > StageTier.SEASON:
            raise ValueError(f"StageEvent tier must be an EVENT or below, got {data.tier}")

    # Properties available before the stage starts

    @property
    def name(self) -> str:
        """The name of the stage event."""
        return self._data.name or self._data.slug.replace("-", " ").title()

    @property
    def end(self) -> Optional[datetime]:
        """The end time of the stage event."""
        return self._data.end

    @cached_property
    def tier(self) -> StageTier:
        """The category of the stage event."""
        self._full_load()
        return self._data.tier

    @property
    def format(self) -> EventFormat:
        """The format of the event, either 'match' or 'stage'."""
        return "stage"

    @cached_property
    def competition(self) -> Optional[Competition]:
        """The competition this event belongs to, if available."""
        from .competition import Competition
        return Competition(self._data.unique_stage, self._provider)

    @cached_property
    def season(self) -> Optional[Season]:
        """The season this event belongs to, if available."""
        node_data = self._data
        while node_data.tier != StageTier.SEASON:
            if not node_data.parent:
                logger.debug(f"No parent stage found while traversing to find season for event {self.id}. Current stage: {node_data.id}, tier: {node_data.tier}")
                return None
            try:
                node_data = self._fetch_entity(node_data.parent.id, self._provider, strict=False)
            except ProviderNotFoundError:
                logger.debug(f"Parent stage with id {node_data.parent.id} not found while traversing to find season for event {self.id}.")
                return None
            if node_data.parent.id == node_data.id:
                logger.debug(f"Reached top level stage without finding season for event {self.id}.")
                return None
        from .season import Season
        return Season(node_data, self._provider)

    @cached_property
    def parent(self) -> Optional[StageEvent]:
        """The parent stage of this stage, if available."""
        self._full_load()
        if self._data.parent:
            parent_data = self._fetch_entity(self._data.parent.id, self._provider, strict=False)
            if parent_data and parent_data.tier > StageTier.SEASON:
                # NOTE - Temporary check to avoid creating StageEvent for parent stages that are season-level or above.
                return StageEvent(parent_data, self._provider)
        return None

    @cached_property
    def substages(self) -> EventCollection:
        """The substages for this event, if available."""
        try:
            return EventCollection([Event(s, self._provider) for s in self._provider.get_stage_substages(self._data.id)])
        except ProviderNotFoundError:
            logger.debug(f"Substages not found for event {self.id}.")
            return EventCollection([])

    @cached_property
    def venue(self) -> Optional[Venue]:
        """The venue where this event takes place, if available."""
        from .venue import Venue
        return Venue(self._data, self._provider)

    @cached_property
    def channels(self) -> EventChannels:
        from .channel import EventChannels
        return EventChannels(self._provider.get_stage_channels(self._data.id), self._provider)

    # Properties available after the stage starts or ends

    @cached_property
    def winner(self) -> Optional[Competitor]:
        """The winner of this event, if available."""
        self._full_load()
        from .competitor import Competitor
        if self._data.winner:
            return Competitor(self._data.winner, self._provider)

    @property
    def standings(self) -> Optional[EntityCollection[Standings]]:
        """The standings for this event, if race and available."""
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

    @overload
    @classmethod
    def _fetch_entity(cls, entity_id: int, provider: SofascoreProvider, strict: Literal[True] = True) -> _StageData: ...

    @overload
    @classmethod
    def _fetch_entity(cls, entity_id: int, provider: SofascoreProvider, strict: Literal[False]) -> Optional[_StageData]: ...

    @classmethod
    def _fetch_entity(cls, entity_id: int, provider: SofascoreProvider, strict: bool = True) -> Optional[_StageData]:
        """Fetch the complete event data from the provider by its raw ID."""
        try:
            return provider.get_stage(entity_id)
        except ProviderNotFoundError:
            logger.debug(f"Stage with id {entity_id} not found during fetch.")
            if strict:
                raise EntityNotFoundError(f"Stage with id {entity_id} not found") from None
        except FetchError as e:
            logger.debug(f"Network error while fetching stage with id {entity_id}: {e}")
            if strict:
                raise DomainError(f"Network error while fetching stage with id {entity_id}") from e
        return None


Event._DOMAIN_MAP = {
    1: MatchEvent,
    2: StageEvent
}


# ===== Event Collection =====

E = TypeVar("E", bound=Event)

class EventCollection(EntityCollection[E]):
    """A specialized collection for handling lists of events with common filtering and sorting needs."""

    @property
    def matches(self) -> EventCollection[MatchEvent]:
        """Return a new EventCollection containing only match events."""
        return EventCollection([e for e in self._entities if isinstance(e, MatchEvent)])

    @property
    def stages(self) -> EventCollection[StageEvent]:
        """Return a new EventCollection containing only stage events."""
        return EventCollection([e for e in self._entities if isinstance(e, StageEvent)])

    def filter_by_date(self, *, before: Optional[date | datetime] = None, after: Optional[date | datetime] = None) -> EventCollection[E]:
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

    def sort_by_date(self, ascending: bool = True) -> EventCollection[E]:
        """Return a new EventCollection sorted by date."""
        return self.__class__(sorted(self._entities, key=lambda e: e.start, reverse=not ascending))

    def filter_by_competitors(self, competitor_ids: list[int]) -> EventCollection[MatchEvent]:
        """Return a new EventCollection containing only match events involving the specified competitor IDs."""
        results = []
        for event in self.matches:
            if event.competitors and ((event.competitors.home.id in competitor_ids) or (event.competitors.away.id in competitor_ids)):
                results.append(event)
        return EventCollection(results)

Events: TypeAlias = EventCollection[Event]


# ===== Event Aware Mixin =====

E = TypeVar("E", bound=Event)

class EventAwareMixin(Generic[E]):
    """
    Toolkit for entities that fetch fixtures and results.
    Provides shared pagination and unified date filtering.
    """

    def get_fixtures(self, silent: bool = False) -> EventCollection[E]:
        """Override in subclass if fixtures are supported."""
        raise NotImplementedError(f"Method get_fixtures must be implemented in the subclass {self.__class__.__name__}")

    def get_results(self, silent: bool = False) -> EventCollection[E]:
        """Override in subclass if results are supported."""
        raise NotImplementedError(f"Method get_results must be implemented in the subclass {self.__class__.__name__}")

    def get_events(self) -> EventCollection[E]:
        """Fetch all events."""
        events: EventCollection[E] = self.get_results(silent=True) + self.get_fixtures(silent=True)
        return events.sort_by_date()

    def _fetch_paginated_events(self, provider_callable: Callable, *args, max_pages: int = 10) -> EventCollection[E]:
        """Internal helper to exhaust a paginated provider endpoint."""
        parsed_events = []
        for page in range(max_pages):
            try:
                events_response: _EventsResponse = provider_callable(*args, page=page)
                parsed_events.extend(events_response.events)
            except ProviderNotFoundError:
                logger.debug(f"No events found for page {page}. Ending pagination.")
                break
            except FetchError as e:
                logger.warning(f"Network error while fetching events for page {page}: {e}. Ending pagination.")
                break

            if not getattr(events_response, "hasNextPage", False):
                break
                
        return EventCollection([Event(e, getattr(self, "_provider")) for e in parsed_events])
