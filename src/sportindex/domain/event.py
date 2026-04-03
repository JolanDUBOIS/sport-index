from __future__ import annotations

from abc import abstractmethod
from functools import cached_property
from pydantic import BaseModel
from datetime import datetime, date
from typing import TYPE_CHECKING, Optional, TypeVar, Generic

from . import logger
from .base import IdentifiableEntity, EntityCollection
from .core import Sport
from .utils import merge_pydantic_models
from sportindex.exceptions import ProviderNotFoundError, FetchError, EntityNotFoundError, DomainError
from sportindex.provider.models import _EventData, _StageData, StageTier

if TYPE_CHECKING:
    from .channel import EventChannels
    from .competition import Competition, Season
    from .competitor import Competitor
    from .incident import Incident
    from .leaderboard import Standings
    from .referee import Referee
    from .venue import Venue
    from sportindex.provider import SofascoreProvider
    from sportindex.provider.models import (
        Round, Score, MatchPeriod, PeriodStats,
        _LineupsResponse, MomentumPoint, EventStatus
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

T = TypeVar("T", _EventData, _StageData)

class Event(IdentifiableEntity[T]):
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
        competition (Competition | None): Competition this event belongs to.
        season (Season): Season this event belongs to.
        venue (Venue | None): Venue where the event takes place.
        channels (EventChannels): TV or streaming channels broadcasting the event.
        winner (Competitor | None): Winner of the event.

    Methods:
        from_id(event_id: int, provider) -> Event: Fetch an event by its unique ID.
    """
    _REPR_FIELDS = ("id", "name", "slug", "start")
    _TYPE_MAP = {_EventData: 1, _StageData: 2}

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
        raise NotImplementedError

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
    def competition(self) -> Optional[Competition]:
        """The competition this event belongs to, if available."""
        raise NotImplementedError

    @property
    @abstractmethod
    def season(self) -> Season:
        """The season this event belongs to."""
        raise NotImplementedError

    @property
    @abstractmethod
    def venue(self) -> Optional[Venue]:
        """The venue where this event takes place, if available."""
        raise NotImplementedError

    @property
    @abstractmethod
    def channels(self) -> EventChannels:
        """Get the channels broadcasting this event."""
        raise NotImplementedError

    @property
    @abstractmethod
    def winner(self) -> Optional[Competitor]:
        """The winner of this event, if available."""
        raise NotImplementedError

    @abstractmethod
    def _full_load(self) -> None:
        """
        Lazy-loads the complete event from the provider.
        Called automatically when accessing properties that require full details
        missing from the initial lightweight API response.
        """
        raise NotImplementedError

    @classmethod
    def from_id(cls, event_id: int, provider: SofascoreProvider) -> Event:
        """Fetch an event by its ID."""
        raw_id, type_idx = cls.decode_id(event_id)
        type_map_reverse = {v: k for k, v in cls._TYPE_MAP.items()}

        if type_idx not in type_map_reverse:
            raise ValueError(f"Invalid event ID {event_id}: unknown type index {type_idx}")

        data_cls = type_map_reverse[type_idx]
        try:
            if data_cls == _EventData:
                parsed_data = provider.get_event(raw_id)
            elif data_cls == _StageData:
                parsed_data = provider.get_stage(raw_id)
            else:
                raise TypeError(f"Unsupported event type index {type_idx} in ID {event_id}")
        except ProviderNotFoundError as e:
            raise EntityNotFoundError(f"Event with id {event_id} not found") from e
        except FetchError as e:
            raise DomainError(f"Network error while fetching event {event_id}") from e

        return cls(parsed_data, provider)


class MatchEvent(Event[_EventData]):
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

    def __init__(self, data: _EventData, provider: SofascoreProvider, **kwargs) -> None:
        if not isinstance(data, _EventData):
            raise TypeError(f"MatchEvent data must be _EventData, got {type(data)}")
        super().__init__(data, provider, **kwargs)

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
    def competition(self) -> Optional[Competition]:
        """The competition this event belongs to, if available."""
        self._full_load()
        from .competition import Competition
        return Competition(self._data.tournament.unique_tournament, self._provider) if self._data.tournament and self._data.tournament.unique_tournament else None

    @cached_property
    def season(self) -> Season:
        """The season this event belongs to."""
        self._full_load()
        from .competition import Season
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

    def _full_load(self) -> None:
        """
        Lazy-loads the complete event from the provider.
        Called automatically when accessing properties that require full details
        missing from the initial lightweight API response.
        """
        if self._full_loaded:
            return
        try:
            self._data = merge_pydantic_models(self._data, self._provider.get_event(self._data.id))
            if not isinstance(self._data, _EventData):
                raise TypeError(f"Event data must be _EventData after full load, got {type(self._data)}")
            self._full_loaded = True
        except ProviderNotFoundError:
            logger.debug(f"Event with id {self._data.id} not found during full load.")
            self._full_loaded = True
        except FetchError as e:
            logger.debug(f"Network error while fully loading event with id {self._data.id}: {e}")
            self._full_loaded = True
        self._clear_cache()


class StageEvent(Event[_StageData]):
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

    def __init__(self, data: _StageData, provider: SofascoreProvider, **kwargs) -> None:
        if not isinstance(data, _StageData):
            raise TypeError(f"StageEvent data must be _StageData, got {type(data)}")
        super().__init__(data, provider, **kwargs)

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
            try:
                node_data = self._provider.get_stage(node_data.parent.id)
            except ProviderNotFoundError:
                logger.debug(f"Parent stage with id {node_data.parent.id} not found while traversing to find season for event {self.id}.")
                return None
            if node_data.parent.id == node_data.id:
                logger.debug(f"Reached top level stage without finding season for event {self.id}.")
                return None
        from .competition import Season
        return Season(node_data, self._provider)

    @cached_property
    def parent(self) -> Optional[StageEvent]: # TODO - NO, I cannot create a stage event if it's a tier SEASON for instance !!! That's a major issue we're facing !!!
        """The parent stage of this stage, if available."""
        self._full_load()
        if self._data.parent:
            parent_data = self._provider.get_stage(self._data.parent.id)
            return StageEvent(parent_data, self._provider) if parent_data else None
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

    def _full_load(self) -> None:
        """
        Lazy-loads the complete event from the provider.
        Called automatically when accessing properties that require full details
        missing from the initial lightweight API response.
        """
        if self._full_loaded:
            return
        try:
            self._data = merge_pydantic_models(self._data, self._provider.get_stage_details(self._data.id))
            if not isinstance(self._data, _StageData):
                raise TypeError(f"Event data must be _StageData after full load, got {type(self._data)}")
            self._full_loaded = True
        except ProviderNotFoundError:
            logger.debug(f"Event with id {self._data.id} not found during full load.")
            self._full_loaded = True
        except FetchError as e:
            logger.debug(f"Network error while fully loading event with id {self._data.id}: {e}")
            self._full_loaded = True
        self._clear_cache()


# ===== Event Collection =====

class MatchEventCollection(EntityCollection[MatchEvent]):
    """A collection specifically for match events, with additional filtering capabilities."""

    def filter_by_competitors(self, competitor_ids: list[int]) -> MatchEventCollection:
        """Return a new MatchEventCollection filtered by competitor IDs."""
        results = []
        for event in self._entities:
            if event.competitors:
                if (event.competitors.home.id in competitor_ids) or (event.competitors.away.id in competitor_ids):
                    results.append(event)
        return self.__class__(results)


class StageEventCollection(EntityCollection[StageEvent]):
    """A collection specifically for stage events."""
    pass


class EventCollection(EntityCollection[Event]):
    """A specialized collection for handling lists of events with common filtering and sorting needs."""

    @property
    def matches(self) -> MatchEventCollection:
        """Return a new MatchEventCollection containing only match events."""
        return MatchEventCollection([e for e in self._entities if isinstance(e, MatchEvent)])

    @property
    def stages(self) -> StageEventCollection:
        """Return a new StageEventCollection containing only stage events."""
        return StageEventCollection([e for e in self._entities if isinstance(e, StageEvent)])

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

    def sort_by_date(self, ascending: bool = True) -> EventCollection:
        """Return a new EventCollection sorted by date."""
        return self.__class__(sorted(self._entities, key=lambda e: e.start, reverse=not ascending))
