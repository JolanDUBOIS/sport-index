from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from functools import cached_property
from typing import TYPE_CHECKING, Generic, overload

import pycountry
from pydantic import ValidationError
from typing_extensions import TypeVar

from sportindex.api_client.models import StageTier, _EventData, _StageData
from sportindex.exceptions import (
    DomainError,
    EntityNotFoundError,
    FetchError,
    ProviderNotFoundError,
)

from .base import DomainModel, IdentifiableEntity
from .collections import EntityCollection, EventCollection

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import datetime

    from sportindex.api_client import SofascoreProvider
    from sportindex.api_client.models import (
        EventStatus,
        MatchPeriod,
        MomentumPoint,
        PeriodStats,
        Round,
        Score,
        _EventsResponse,
        _LineupsResponse,
    )

    from .channel import Channel
    from .competition import Competition
    from .competitor import Athlete, Competitor
    from .core import Sport
    from .incident import Incident
    from .leaderboard import Standings
    from .referee import Referee
    from .season import Season
    from .venue import Venue

logger = logging.getLogger(__name__)


# ===== Event entity =====

class Event(IdentifiableEntity):
    """Something that happens at a point in time — a football match, a tennis match, a race.

    The common base of the two event kinds. Instantiating `Event` returns whichever the
    payload describes: a `MatchEvent` (two competitors facing each other) or a `StageEvent`
    (a stage, session or race within a competition). Both are public and documented in their
    own right; this class holds what they share.

    Attributes:
        id (str): Globally unique SDK ID — "mch:<id>" for matches, "stg:<id>" for stages.
        name (str): Display name, e.g. "Paris Saint Germain Marseille".
        slug (str): URL-friendly identifier, e.g. "paris-saint-germain-marseille".
        start (datetime | None): When the event starts. Always set for a `MatchEvent`; a
            `StageEvent` may have none, since the provider leaves undated stages open.
        status (EventStatus | None): Whether the event is scheduled, live or finished, if the
            provider states it.
        sport (Sport | None): The sport this event belongs to, taken from its season. None
            when the season is unknown.
        competition (Competition | None): The competition this event is part of, if the
            provider states it. Defined by each subclass.
        season (Season | None): The season this event is part of, if the provider states it.
            Defined by each subclass.
        venue (Venue | None): Where the event takes place. Defined by each subclass; a
            `StageEvent` always has one, since its circuit is part of the stage itself.
        winner (Competitor | None): Who won, once decided. Defined by each subclass.
        source (_EventData | _StageData): The parsed payload backing this entity.
            (inherited from BaseEntity)

    Methods:
        get_channels(country: str) -> EntityCollection[Channel]: The TV channels broadcasting
            this event in `country`, given as a name, alpha-2 or alpha-3 code. Empty when the
            event is not broadcast there or no broadcast data exists.
        from_id(entity_id: str, provider: SofascoreProvider) -> Event: The event with this SDK
            ID; the prefix decides whether a `MatchEvent` or `StageEvent` is built.
            (classmethod, inherited from IdentifiableEntity)

    Raises:
        TypeError: If constructed with data that is neither `_EventData` nor `_StageData`.
        ValueError: If `get_channels` is given a country string that matches no ISO 3166-1 record.
        EntityNotFoundError: If `from_id` names an event the provider does not have.
        DomainError: If the provider fails with a network or transport error.
    """
    _data: _EventData | _StageData
    _REPR_FIELDS = ("id", "name", "slug", "start")

    @overload
    def __new__(cls, data: _EventData, provider: SofascoreProvider, **kwargs) -> MatchEvent: ...

    @overload
    def __new__(cls, data: _StageData, provider: SofascoreProvider, **kwargs) -> StageEvent: ...

    def __new__(cls, data: _EventData | _StageData, provider: SofascoreProvider, **kwargs):
        """Create the correct subclass based on the data type."""
        if cls is Event:
            if isinstance(data, _EventData):
                return super().__new__(MatchEvent)
            if isinstance(data, _StageData):
                return super().__new__(StageEvent)
        return super().__new__(cls)

    def __init__(self, data: _EventData | _StageData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, (_EventData, _StageData)):
            raise TypeError(f"Event data must be either _EventData or _StageData, got {type(data)}")

        self._full_loaded = False

    @property
    def id(self) -> str:
        """The unique ID of the event."""
        return self.encode_id(self._data.id)

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
    def start(self) -> datetime | None:
        """The start time of the event, if the provider has dated it."""
        return self._data.start

    @property
    def status(self) -> EventStatus | None:
        """The status of the event, if available."""
        return self._data.status

    @property
    def sport(self) -> Sport | None:
        """The sport this event belongs to."""
        return self.season.sport if self.season else None

    @property
    @abstractmethod
    def competition(self) -> Competition | None:
        """The competition this event belongs to, if available."""
        raise NotImplementedError("Property competition must be implemented in subclasses")

    @property
    @abstractmethod
    def season(self) -> Season | None:
        """The season this event belongs to, if available."""
        raise NotImplementedError("Property season must be implemented in subclasses")

    @property
    @abstractmethod
    def venue(self) -> Venue | None:
        """The venue where this event takes place, if available."""
        raise NotImplementedError("Property venue must be implemented in subclasses")

    @property
    @abstractmethod
    def winner(self) -> Competitor | None:
        """The winner of this event, if available."""
        raise NotImplementedError("Property winner must be implemented in subclasses")

    def get_channels(self, country: str) -> EntityCollection[Channel]:
        """
        Fetch the channels broadcasting this event in a specific country.
        Country can be specified as a name, alpha-2, or alpha-3 code.
        """
        try:
            all_channels = self._get_all_channels()
        except ProviderNotFoundError:
            logger.debug(f"No channel data available for event {self.id}.")
            return EntityCollection()

        try:
            parsed = pycountry.countries.lookup(country)
            alpha = parsed.alpha_2
        except LookupError as e:
            raise ValueError(f"Could not resolve '{country}' to a valid country using pycountry.") from e

        if alpha not in all_channels:
            logger.debug(f"Country '{country}' (alpha-2: '{alpha}') not found in channels for event {self.id}. Available countries: {list(all_channels.keys())}")
            return EntityCollection()

        from .channel import Channel
        channel_ids = all_channels[alpha]
        return EntityCollection([Channel.from_id(cid, self._provider) for cid in channel_ids])

    @abstractmethod
    def _get_all_channels(self) -> dict[str, list[int]]:
        """Fetch all channels broadcasting this event, organized by country."""
        raise NotImplementedError("Method _get_all_channels must be implemented in subclasses")


class MatchEvent(Event):
    """A match between two competitors — a football fixture, a tennis match, an MMA bout.

    Everything `Event` offers is available here too. The members below are what a match adds:
    two named sides, a score, and the in-game detail that comes with them. Most of that
    detail only exists once the match has started, and much of it — lineups, statistics,
    momentum — is only published for major competitions; expect empty collections and None
    elsewhere.

    Attributes:
        round (Round | None): Which round of the competition this match belongs to, if the
            provider states it.
        referee (Referee | None): The official in charge, if the provider names one.
        competitors (MatchCompetitors): The home and away sides.
        score (Score | None): Home and away scores. None before the match produces one, and
            also when the provider renders the score non-numerically.
        periods (list[MatchPeriod]): Per-period breakdown — halves, sets, overtime, penalty
            shootout — each with its own score and timing. Empty when unavailable.
        lineups (MatchLineups | None): The starting eleven, or equivalent, for each side.
            None when the provider publishes no lineups for this match.
        incidents (list[Incident]): What happened during the match — goals, cards,
            substitutions, VAR decisions, period boundaries. Empty when unavailable. Reflects
            the live state on each access rather than being cached.
        statistics (list[PeriodStats]): Team statistics grouped by period, e.g. possession and
            shots. Empty when unavailable.
        momentum_graph (list[MomentumPoint]): Minute-by-minute pressure values, positive
            towards the home side. Empty when unavailable. Reflects the live state on each
            access rather than being cached.
        h2h (EventCollection[MatchEvent]): Previous meetings between these two competitors.
            Empty when the provider has no head-to-head record.
        id (str): Globally unique SDK ID, of the form "mch:<id>". (inherited from Event)
        start (datetime): Kick-off time. Always set for a match. (inherited from Event)
        name, slug, status, sport, competition, season, venue, winner: See `Event`.
        source (_EventData): The parsed payload backing this entity. (inherited from BaseEntity)

    Methods:
        get_channels(country: str) -> EntityCollection[Channel]: The TV channels broadcasting
            this match in `country`. (inherited from Event)
        from_id(entity_id: str, provider: SofascoreProvider) -> MatchEvent: The match with this
            SDK ID. (classmethod, inherited from IdentifiableEntity)

    Raises:
        TypeError: If constructed with data that is not `_EventData`.
        EntityNotFoundError: If `from_id` names a match the provider does not have.
        DomainError: If the provider fails with a network or transport error.
    """
    _data: _EventData
    _PREFIX: str = "mch"
    _REPR_FIELDS = ("id", "name", "slug", "round", "start")

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
    def start(self) -> datetime:
        """The kick-off time of the match. Always present, unlike a stage's."""
        return self._data.start

    @property
    def round(self) -> Round | None:
        """The round of the match event, if available."""
        return self._data.round

    @cached_property
    def competition(self) -> Competition | None:
        """The competition this event belongs to, if available."""
        self._full_load()
        from .competition import Competition
        return Competition(self._data.tournament.unique_tournament, self._provider) if self._data.tournament and self._data.tournament.unique_tournament else None

    @cached_property
    def season(self) -> Season | None:
        """The season this event belongs to."""
        self._full_load()
        from .season import Season
        return Season(
            self._data.season,
            self._provider,
            uniqueTournament=self._data.tournament.unique_tournament
        ) if self._data.season and self._data.tournament and self._data.tournament.unique_tournament else None

    @cached_property
    def referee(self) -> Referee | None:
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
    def venue(self) -> Venue | None:
        """The venue where this event takes place, if available."""
        self._full_load()
        if self._data.venue is None:
            return None
        from .venue import Venue
        return Venue(self._data.venue, self._provider)

    # Properties available after the match starts or ends

    @property
    def score(self) -> Score | None:
        """The score for this event, if available and numeric."""
        if self._data.home.score is None or self._data.away.score is None:
            return None
        from sportindex.api_client.models import Score
        try:
            return Score(
                home=self._data.home.score,
                away=self._data.away.score
            )
        except ValidationError:
            logger.debug(f"Non-numeric score for event {self.id}: home={self._data.home.score!r}, away={self._data.away.score!r}")
            return None

    @property
    def winner(self) -> Competitor | None:
        """The winner of this event, if available."""
        self._full_load()
        winner_code = self._data.winner_code
        if winner_code == 1:
            return self.competitors.home
        if winner_code == 2:
            return self.competitors.away
        return None

    @property
    def periods(self) -> list[MatchPeriod]:
        """The periods for this event, if available."""
        self._full_load()
        return self._data.periods.periods if self._data.periods else []

    @cached_property
    def lineups(self) -> MatchLineups | None:
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

    @staticmethod
    def _fetch_entity(raw_id: int, provider: SofascoreProvider, **kwargs) -> _EventData:
        """Fetch the event data from the provider by its raw ID."""
        try:
            return provider.get_event(raw_id)
        except ProviderNotFoundError as e:
            logger.debug(f"Event with id {raw_id} not found: {e}")
            raise EntityNotFoundError(f"Event with id {raw_id} not found") from e
        except FetchError as e:
            logger.error(f"Network error while fetching event with id {raw_id}: {e}")
            raise DomainError(f"Network error while fetching event with id {raw_id}") from e


class StageEvent(Event):
    """A stage, session or race within a competition — a Grand Prix, a qualifying session, a Tour stage.

    Everything `Event` offers is available here too. The members below are what a stage adds.
    Stages nest: a Grand Prix weekend contains practice, qualifying and the race itself, each
    a `StageEvent` in its own right, distinguished by `tier`. The season at the top of that
    chain is a `Season`, not a `StageEvent`, so `parent` is None for a top-level stage even
    though `season` is not.

    Attributes:
        end (datetime | None): When the stage finishes, if the provider states it.
        tier (StageTier | None): How deep in the nesting this stage sits — EVENT, PRACTICE,
            QUALIFYING, RACE, LAP, STAGE, and so on. Always below SEASON when present; None
            when the provider does not classify the stage.
        parent (StageEvent | None): The stage containing this one, or None if this stage
            hangs directly off its season.
        substages (EventCollection[StageEvent]): The stages contained within this one. Empty
            for a leaf stage such as a single race.
        standings (list[Standings]): Exactly two ranking tables for this stage — competitors
            and teams — each empty if the provider publishes nothing for it.
        venue (Venue): The circuit or course, derived from the stage itself rather than
            looked up separately. Never None, though its fields may be empty.
        id (str): Globally unique SDK ID, of the form "stg:<id>". (inherited from Event)
        start (datetime | None): When the stage begins. None for a stage the provider has not
            yet dated — a common case for future rounds. (inherited from Event)
        name, slug, status, sport, competition, season, winner: See `Event`.
        source (_StageData): The parsed payload backing this entity. (inherited from BaseEntity)

    Methods:
        get_channels(country: str) -> EntityCollection[Channel]: The TV channels broadcasting
            this stage in `country`. (inherited from Event)
        from_id(entity_id: str, provider: SofascoreProvider) -> StageEvent: The stage with this
            SDK ID. (classmethod, inherited from IdentifiableEntity)

    Raises:
        TypeError: If constructed with data that is not `_StageData`.
        ValueError: If constructed with a tier of SEASON or above — such data describes a
            `Season`, not an event — or if a parent stage resolves to an invalid tier.
        EntityNotFoundError: If `from_id` names a stage the provider does not have.
        DomainError: If the provider fails with a network or transport error.
    """
    _data: _StageData
    _PREFIX: str = "stg"
    _REPR_FIELDS = ("id", "name", "slug", "tier", "start", "end")

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
    def tier(self) -> StageTier | None:
        """The category of the stage event, if the provider states it."""
        self._full_load()
        return self._data.tier

    @property
    def end(self) -> datetime | None:
        """The end time of the stage event."""
        return self._data.end

    @cached_property
    def competition(self) -> Competition | None:
        """The competition this event belongs to, if available."""
        self._full_load()
        from .competition import Competition
        return Competition(self._data.unique_stage, self._provider) if self._data.unique_stage else None

    @cached_property
    def _parent(self) -> StageEvent | Season | None:
        """The parent stage or season of this stage, if available."""
        self._full_load()
        if not self._data.parent:
            return None

        parent_entity = self._fetch_entity(self._data.parent.id, self._provider)
        if parent_entity.tier == StageTier.SEASON:
            from .season import Season
            return Season(parent_entity, self._provider)
        if parent_entity.tier > StageTier.SEASON:
            return StageEvent(parent_entity, self._provider)
        raise ValueError(f"Invalid tier {parent_entity.tier} for parent of stage event {self.id}.",
                         f"Expected a tier SEASON or below, got {parent_entity.tier}")

    @cached_property
    def parent(self) -> StageEvent | None:
        """The parent stage of this stage, if available."""
        if self._parent and isinstance(self._parent, StageEvent):
            return self._parent
        return None

    @cached_property
    def season(self) -> Season | None:
        """The season this event belongs to, if available."""
        from .season import Season
        if self._parent and isinstance(self._parent, Season):
            return self._parent
        if self.parent:
            return self.parent.season
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
    def venue(self) -> Venue:
        """The venue where this event takes place."""
        from .venue import Venue
        return Venue(self._data, self._provider)

    # Properties available after the stage starts or ends

    @cached_property
    def winner(self) -> Competitor | None:
        """The winner of this event, if available."""
        self._full_load()
        from .competitor import Competitor
        if self._data.winner:
            return Competitor(self._data.winner, self._provider)
        return None

    @property
    def standings(self) -> list[Standings]:
        """The competitors and teams standings for this event; either may be empty."""
        from sportindex.api_client.models import _RacingStandingsData
        try:
            competitors_standings = self._provider.get_stage_standings_competitors(self._data.id)
        except ProviderNotFoundError as e:
            logger.debug(f"Failed to fetch competitors standings for event {self.id}: {e}")
            competitors_standings = _RacingStandingsData()
        try:
            teams_standings = self._provider.get_stage_standings_teams(self._data.id)
        except ProviderNotFoundError as e:
            logger.debug(f"Failed to fetch teams standings for event {self.id}: {e}")
            teams_standings = _RacingStandingsData()
        from .leaderboard import Standings
        return [
            Standings(competitors_standings, self._provider, name=f"Competitors {self.name}", kind="competitors"),
            Standings(teams_standings, self._provider, name=f"Teams {self.name}", kind="teams")
        ]

    def _get_all_channels(self) -> dict[str, list[int]]:
        """Fetch all channels broadcasting this event, organized by country."""
        return self._provider.get_stage_channels(self._data.id).channels

    @staticmethod
    def _fetch_entity(raw_id: int, provider: SofascoreProvider, **kwargs) -> _StageData:
        """Fetch the stage event data from the provider by its raw ID."""
        try:
            return provider.get_stage(raw_id)
        except ProviderNotFoundError as e:
            logger.debug(f"Stage event with id {raw_id} not found: {e}")
            raise EntityNotFoundError(f"Stage event with id {raw_id} not found") from e
        except FetchError as e:
            logger.error(f"Network error while fetching stage event with id {raw_id}: {e}")
            raise DomainError(f"Network error while fetching stage event with id {raw_id}") from e


# ===== Components =====

class MatchCompetitors(DomainModel):
    """The two sides of a `MatchEvent`.

    Attributes:
        home (Competitor): The home side, or the first-named competitor at a neutral venue.
        away (Competitor): The away side, or the second-named competitor at a neutral venue.
    """
    home: Competitor
    away: Competitor


class MatchLineups(DomainModel):
    """The lineups of both sides of a `MatchEvent`.

    Attributes:
        home (list[Athlete]): The players listed for the home side.
        away (list[Athlete]): The players listed for the away side.
    """
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
    """Mixin giving an entity a calendar of upcoming and past events.

    Mixed into `Channel`, `Competitor` (and `Team` / `Athlete`), `Manager`, `Referee`,
    `Season` and `Venue`. Each supplies its own `get_fixtures` and `get_results`; some have
    no endpoint for one or the other and return an empty collection, which is why both take
    a `silent` flag to suppress the warning that goes with it.

    Where the provider paginates, pages are followed until it reports no more, up to a cap of
    ten — so a very long history comes back truncated rather than complete.

    Methods:
        get_fixtures(silent: bool = False) -> EventCollection[E]: The entity's upcoming events.
            Abstract; each entity implements it. Logs a warning when it cannot be supported,
            unless `silent` is True.
        get_results(silent: bool = False) -> EventCollection[E]: The entity's past events.
            Abstract; each entity implements it. Same warning behaviour.
        get_events() -> EventCollection[E]: Fixtures and results in one collection, sorted by
            start time, oldest first, with undated events last. Suppresses the
            unsupported-endpoint warnings.
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

            if not events_response.has_next_page:
                break

        return EventCollection([Event(e, self._provider) for e in parsed_events])
