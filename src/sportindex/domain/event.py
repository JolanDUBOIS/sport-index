from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cached_property
from datetime import datetime
from typing import (
    TYPE_CHECKING, Optional,
    Generic, Callable, ClassVar,
    Literal, Self, overload
)

import pycountry
from pydantic import BaseModel
from typing_extensions import TypeVar

from . import logger
from .base import IdentifiableEntity
from .collections import EventCollection, EntityCollection
from .core import Sport
from .types import SportContestNature
from .utils import merge_pydantic_models
from sportindex.exceptions import ProviderNotFoundError, FetchError, EntityNotFoundError, DomainError
from sportindex.provider.models import _EventData, _StageData, StageTier

if TYPE_CHECKING:
    from .channel import Channel
    from .competition import Competition
    from .competitor import Competitor, Athlete
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
        winner (Competitor | None): Winner of the event.

    Methods:
        from_id(event_id: int, provider) -> Event: Fetch an event by its unique ID.
    """
    _data: _EventData | _StageData
    _REPR_FIELDS = ("id", "name", "slug", "start")
    _N_TYPES: int = 2
    _REGISTRY: dict[int, type[Event]] = {}
    _TYPE_IDX: int
    sport_nature: ClassVar[SportContestNature]

    def __init_subclass__(cls, **kwargs):
        """Automatically registers subclasses when the file is loaded."""
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "_TYPE_IDX"):
            Event._REGISTRY[cls._TYPE_IDX] = cls

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
        return self.encode_id(self._data.id, type(self)._TYPE_IDX)

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
    def sport(self) -> Sport[Self]:
        """The sport this event belongs to."""
        return self.season.sport

    @property
    @abstractmethod
    def competition(self) -> Optional[Competition]:
        """The competition this event belongs to, if available."""
        raise NotImplementedError("Property competition must be implemented in subclasses")

    @property
    @abstractmethod
    def season(self) -> Optional[Season]:
        """The season this event belongs to, if available."""
        raise NotImplementedError("Property season must be implemented in subclasses")

    @property
    @abstractmethod
    def venue(self) -> Optional[Venue]:
        """The venue where this event takes place, if available."""
        raise NotImplementedError("Property venue must be implemented in subclasses")

    @property
    @abstractmethod
    def winner(self) -> Optional[Competitor]:
        """The winner of this event, if available."""
        raise NotImplementedError("Property winner must be implemented in subclasses")

    def get_channels(self, country: str) -> EntityCollection[Channel]:
        """
        Fetch the channels broadcasting this event in a specific country.
        Country can be specified as a name, alpha-2, or alpha-3 code.
        """
        all_channels = self._get_all_channels()

        try:
            parsed = pycountry.countries.lookup(country)
            alpha = parsed.alpha_2 
        except LookupError:
            raise ValueError(f"Could not resolve '{country}' to a valid country using pycountry.")

        if alpha not in all_channels:
            logger.debug(f"Country '{country}' (alpha-2: '{alpha}') not found in channels for event {self.id}. Available countries: {list(all_channels.keys())}")
            return EntityCollection()

        channel_ids = all_channels[alpha]
        return EntityCollection([Channel.from_id(cid, self._provider) for cid in channel_ids])

    @abstractmethod
    def _get_all_channels(self) -> dict[str, list[int]]:
        """Fetch all channels broadcasting this event, organized by country."""
        raise NotImplementedError("Method _get_all_channels must be implemented in subclasses")

    def _full_load(self) -> None:
        """
        Lazy-loads the complete event from the provider.
        Called automatically when accessing properties that require full details
        missing from the initial lightweight API response.
        """
        if self._full_loaded:
            return

        self._data = merge_pydantic_models(self._data, self._fetch_entity(self.id, self._provider, strict=False))

        self._full_loaded = True
        self._clear_cache()

    @classmethod
    def from_id(cls, event_id: int, provider: SofascoreProvider) -> Self:
        """Fetch an event by its ID."""
        entity_data = cls._fetch_entity(event_id, provider)

        instance = cls(entity_data, provider)
        if not issubclass(type(instance), cls):
            raise TypeError(
                f"ID {event_id} belongs to a {type(instance).__name__}, but was initialized as a {cls.__name__}. "
                f"Use {type(instance).__name__}.from_id() instead."
            )
        return instance

    @overload
    @classmethod
    def _fetch_entity(cls, event_id: int, provider: SofascoreProvider, strict: Literal[True] = True) -> _EventData | _StageData: ...

    @overload
    @classmethod
    def _fetch_entity(cls, event_id: int, provider: SofascoreProvider, strict: Literal[False]) -> Optional[_EventData | _StageData]: ...

    @classmethod
    def _fetch_entity(cls, event_id: int, provider: SofascoreProvider, strict: bool = True) -> Optional[_EventData | _StageData]:
        """Fetch the complete event data from the provider by its ID."""
        _, type_idx = cls.decode_id(event_id)
        target_subclass = cls._REGISTRY.get(type_idx)
        if not target_subclass:
            raise TypeError(f"Invalid event ID {event_id}: unknown type index {type_idx}")
        return target_subclass._fetch_entity(event_id, provider, strict=strict)


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
    _REPR_FIELDS = ("id", "name", "slug", "round", "format", "start")
    _TYPE_IDX = 1
    sport_nature: ClassVar[SportContestNature] = SportContestNature.OPPOSITION

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

    @cached_property
    def competition(self) -> Optional[Competition]:
        """The competition this event belongs to, if available."""
        self._full_load()
        from .competition import Competition
        return Competition(self._data.tournament.unique_tournament, self._provider) if self._data.tournament and self._data.tournament.unique_tournament else None

    @cached_property
    def season(self) -> Season[MatchEvent]:
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
    def h2h(self) -> EventCollection[MatchEvent]:
        """Head-to-head history for the competitors in this event, if available."""
        try:
            return EventCollection([MatchEvent(e, self._provider) for e in self._provider.get_h2h_history(self._data.custom_id).events])
        except ProviderNotFoundError:
            logger.debug(f"H2H history not found for event {self.id}.")
            return EventCollection()

    def _get_all_channels(self) -> dict[str, list[int]]:
        """Fetch all channels broadcasting this event, organized by country."""
        return self._provider.get_event_channels(self._data.id).channels

    @overload
    @classmethod
    def _fetch_entity(cls, event_id: int, provider: SofascoreProvider, strict: Literal[True] = True) -> _EventData: ...

    @overload
    @classmethod
    def _fetch_entity(cls, event_id: int, provider: SofascoreProvider, strict: Literal[False]) -> Optional[_EventData]: ...

    @classmethod
    def _fetch_entity(cls, event_id: int, provider: SofascoreProvider, strict: bool = True) -> Optional[_EventData]:
        """Fetch the complete event data from the provider by its ID."""
        raw_id, type_idx = cls.decode_id(event_id)
        if type_idx != cls._TYPE_IDX:
            raise TypeError(f"Invalid event ID {event_id}: expected type index {cls._TYPE_IDX}, got {type_idx}")

        try:
            return cls._fetch_raw_event(raw_id, provider)

        except ProviderNotFoundError:
            logger.debug(f"Event with ID {event_id} not found during fetch")
            if strict:
                raise EntityNotFoundError(f"Event with ID {event_id} not found during fetch") from None

        except FetchError as e:
            logger.debug(f"Network error while fetching event with ID {event_id}: {e}")
            if strict:
                raise DomainError(f"Network error while fetching event with ID {event_id}") from e

        return None

    @staticmethod
    def _fetch_raw_event(raw_event_id: int, provider: SofascoreProvider) -> Optional[_EventData]:
        """Fetch the raw event data from the provider by its raw ID."""
        return provider.get_event(raw_event_id)


class StageEvent(Event):
    """An event representing a specific stage, phase, or race within a competition.
    
    Provides access to stage-specific properties like tiers, parent-child relationships, 
    and team/competitor standings.

    Attributes:
        end (datetime | None): The scheduled end time of the stage.
        tier (StageTier): The categorization tier of the stage.
        parent (StageEvent | None): The overarching parent stage, if applicable.
        substages (EventCollection): Any child stages contained within this stage.
        standings (list[Standings] | None): The rankings for competitors and teams.
    """
    _data: _StageData
    _REPR_FIELDS = ("id", "name", "slug", "tier", "format", "start", "end")
    _TYPE_IDX = 2
    sport_nature: ClassVar[SportContestNature] = SportContestNature.COMPARISON

    def __init__(self, data: _StageData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _StageData):
            raise TypeError(f"StageEvent data must be _StageData, got {type(data)}")
        if data.tier and data.tier <= StageTier.SEASON:
            raise ValueError(f"StageEvent tier must be an EVENT or below, got {data.tier}")

    # Properties available before the stage starts

    @property
    def name(self) -> str:
        """The name of the stage event."""
        return self._data.name or self._data.slug.replace("-", " ").title()

    @cached_property
    def tier(self) -> StageTier:
        """The category of the stage event."""
        self._full_load()
        return self._data.tier

    @property
    def end(self) -> Optional[datetime]:
        """The end time of the stage event."""
        return self._data.end

    @cached_property
    def competition(self) -> Optional[Competition]:
        """The competition this event belongs to, if available."""
        self._full_load()
        from .competition import Competition
        return Competition(self._data.unique_stage, self._provider)

    @cached_property
    def _parent(self) -> Optional[StageEvent | Season]:
        """The parent stage or season of this stage, if available."""
        self._full_load()
        if self._data.parent:
            try:
                parent_id = self.encode_id(self._data.parent.id, self._TYPE_IDX)
                return self.__class__.from_id(parent_id, self._provider)
            except ValueError:
                try:
                    from .competition import Competition
                    from .season import Season
                    parent_id = Season.encode_id(
                        self._data.parent.id,
                        Season._TYPE_MAP[_StageData],
                        Competition.encode_id(self._data.unique_stage.id, 2)
                    )
                    return Season.from_id(parent_id, self._provider)
                except ValueError:
                    logger.debug(f"Parent stage with ID {self._data.parent.id} not found as stage or season while fetching parent for stage event {self.id}.")
        return None

    @cached_property
    def parent(self) -> Optional[StageEvent]:
        """The parent stage of this stage, if available."""
        if self._parent and isinstance(self._parent, StageEvent):
            return self._parent
        return None

    @cached_property
    def season(self) -> Optional[Season[StageEvent]]:
        """The season this event belongs to, if available."""
        from .season import Season
        if self._parent and isinstance(self._parent, Season):
            return self._parent
        return None

    @cached_property
    def substages(self) -> EventCollection[StageEvent]:
        """The substages for this event, if available."""
        try:
            return EventCollection([Event(s, self._provider) for s in self._provider.get_stage_substages(self._data.id)])
        except ProviderNotFoundError:
            logger.debug(f"Substages not found for event {self.id}.")
            return EventCollection()

    @cached_property
    def venue(self) -> Optional[Venue]:
        """The venue where this event takes place, if available."""
        from .venue import Venue
        return Venue(self._data, self._provider)

    # Properties available after the stage starts or ends

    @cached_property
    def winner(self) -> Optional[Competitor]:
        """The winner of this event, if available."""
        self._full_load()
        from .competitor import Competitor
        if self._data.winner:
            return Competitor(self._data.winner, self._provider)

    @property
    def standings(self) -> Optional[list[Standings]]:
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
        return [
            Standings(competitors_standings, self._provider, name=f"Competitors {self.name}", kind="competitors"),
            Standings(teams_standings, self._provider, name=f"Teams {self.name}", kind="teams")
        ]

    def _get_all_channels(self) -> dict[str, list[int]]:
        """Fetch all channels broadcasting this event, organized by country."""
        return self._provider.get_stage_channels(self._data.id).channels

    @overload
    @classmethod
    def _fetch_entity(cls, event_id: int, provider: SofascoreProvider, strict: Literal[True] = True) -> _StageData: ...

    @overload
    @classmethod
    def _fetch_entity(cls, event_id: int, provider: SofascoreProvider, strict: Literal[False]) -> Optional[_StageData]: ...

    @classmethod
    def _fetch_entity(cls, event_id: int, provider: SofascoreProvider, strict: bool = True) -> Optional[_StageData]:
        """Fetch the complete event data from the provider by its ID."""
        raw_id, type_idx = cls.decode_id(event_id)
        if type_idx != cls._TYPE_IDX:
            raise TypeError(f"Invalid event ID {event_id}: expected type index {cls._TYPE_IDX}, got {type_idx}")

        try:
            return provider.get_stage(raw_id)

        except ProviderNotFoundError:
            logger.debug(f"Stage with ID {event_id} not found during fetch")
            if strict:
                raise EntityNotFoundError(f"Stage with ID {event_id} not found during fetch") from None

        except FetchError as e:
            logger.debug(f"Network error while fetching stage with ID {event_id}: {e}")
            if strict:
                raise DomainError(f"Network error while fetching stage with ID {event_id}") from e

        return None

    @staticmethod
    def _fetch_raw_stage(stage_id: int, provider: SofascoreProvider) -> Optional[_StageData]:
        """Fetch the raw stage data from the provider by its raw ID."""
        return provider.get_stage(stage_id)


# ===== Components =====

class MatchCompetitors(BaseModel):
    """Represents the two competitors in a match."""
    home: Competitor
    away: Competitor


class MatchLineups(BaseModel):
    """Represents the lineups of both teams for a match."""
    home: list[Athlete]
    away: list[Athlete]

    @classmethod
    def _from_base_schema(cls, lineup_response: _LineupsResponse, provider: SofascoreProvider) -> MatchLineups:
        """Create MatchLineups from a _LineupsResponse."""
        from .competitor import Athlete
        if not lineup_response or not lineup_response.home or not lineup_response.away:
            logger.debug(f"Lineups response is incomplete for event. Response: {lineup_response}")
            raise ProviderNotFoundError("Lineups data is incomplete or missing")
        return cls(
            home=[Athlete(p, provider) for p in lineup_response.home.players],
            away=[Athlete(p, provider) for p in lineup_response.away.players]
        )


# ===== Event Aware Mixin =====

E = TypeVar("E", bound="Event", default="Event")

class EventAwareMixin(ABC, Generic[E]):
    """
    Toolkit for entities that fetch fixtures and results. Provides shared pagination and unified date filtering.

    Methods:
        get_fixtures(silent=False) -> EventCollection[E]: Fetch upcoming fixtures.
        get_results(silent=False) -> EventCollection[E]: Fetch past results.
        get_events() -> EventCollection[E]: Fetch all events (fixtures + results), sorted by date.
    """

    @abstractmethod
    def get_fixtures(self, silent: bool = False) -> EventCollection[E]:
        """Override in subclass if fixtures are supported."""
        raise NotImplementedError(f"Method get_fixtures must be implemented in the subclass {self.__class__.__name__}")

    @abstractmethod
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
