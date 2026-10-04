from __future__ import annotations

import logging
from abc import abstractmethod
from datetime import date  # noqa: TC003
from functools import cached_property
from typing import TYPE_CHECKING, overload

from nameparser import HumanName

from sportindex.api_client.models import Amount, _PlayerData, _TeamData
from sportindex.exceptions import (
    DomainError,
    EntityNotFoundError,
    FetchError,
    ProviderNotFoundError,
)

from .base import DomainModel, SearchableMixin
from .collections import EntityCollection, ScoredEntityCollection
from .event import EventAwareMixin

if TYPE_CHECKING:
    from sportindex.api_client import SofascoreProvider
    from sportindex.api_client.models import _PlayerTeamInfoData

    from .core import Country, Sport
    from .enums import Gender
    from .event import EventCollection
    from .manager import Manager
    from .venue import Venue

logger = logging.getLogger(__name__)


#: The provider's `type` for a team-shaped record that describes one person — a tennis player,
#: a driver, a rider, a fighter. Clubs and national teams are 0, doubles pairs 2. Inferred from
#: recorded payloads; the provider does not document it.
_INDIVIDUAL = 1


def _is_individual(data: _TeamData) -> bool:
    """Whether a team-shaped record describes one person rather than a team.

    The provider's `type` decides. A record without one (the clubs embedded in player
    search results) is an athlete only if it carries athlete details.
    """
    if data.type is not None:
        return data.type == _INDIVIDUAL
    return data.player_team_info is not None


def _competitor_class(data: _TeamData | _PlayerData) -> type[Team | Athlete]:
    """The concrete class a competitor payload is built as."""
    if isinstance(data, _PlayerData):
        return _PlayerAthlete
    if isinstance(data, _TeamData):
        return _TeamAthlete if _is_individual(data) else Team
    raise TypeError(f"Competitor data must be either _TeamData or _PlayerData, got {type(data)}")


class Competitor(SearchableMixin, EventAwareMixin):
    """Whoever takes one side of an event — a club, a national team, a driver, a tennis player.

    `Competitor` is never instantiated as such: constructing one returns a `Team` or an
    `Athlete`, decided from the payload alone, without a request. The same entity therefore
    has the same class and ID however it is reached — as a side of a match, a standings row,
    a search result, or by ID. The members below are common to both.

    Attributes:
        id (str): Globally unique SDK ID, that of the `Team` or `Athlete` it is.
        name (str): Display name, e.g. "Paris Saint-Germain", "Carlos Alcaraz".
        slug (str): URL-friendly identifier, e.g. "paris-saint-germain".
        short_name (str): Abbreviated name, e.g. "PSG", "C. Alcaraz". Falls back to `name`
            when the provider supplies none.
        full_name (str): The unabbreviated name — the team's full legal name, or a player's
            first and last name joined. Falls back to `name`.
        gender (Gender | None): The competitor's gender, if the provider states it.
        country (Country | None): The country the competitor represents or is based in, if
            the provider states it.
        sport (Sport | None): The sport this competitor plays. None only for a player-shaped
            competitor with no team on record.
        source (_TeamData | _PlayerData): The parsed payload backing this entity.
            (inherited from BaseEntity)

    Methods:
        get_fixtures(silent: bool = False) -> EventCollection: The competitor's upcoming events.
            Always empty for a player in a team sport: the provider has no fixtures endpoint
            for them. Logs a warning in that case unless `silent` is True.
        get_results(silent: bool = False) -> EventCollection: The competitor's past events.
        get_events() -> EventCollection: Fixtures and results combined, sorted by start time.
            (inherited from EventAwareMixin)
        search(query: str, provider: SofascoreProvider, max_results: int = 20) -> ScoredEntityCollection[Competitor]:
            Teams and athletes matching `query` in one collection, sorted by relevance and
            capped at `max_results`. (classmethod)
        from_id(entity_id: str, provider: SofascoreProvider) -> Competitor: The competitor with
            this SDK ID. (classmethod, inherited from IdentifiableEntity)

    Raises:
        TypeError: If constructed with data that is neither `_TeamData` nor `_PlayerData`.
        ValueError: If `search` is given an empty query.
        EntityNotFoundError: If `from_id` names a competitor the provider does not have.
        DomainError: If the provider fails with a network or transport error.
    """
    _data: _TeamData | _PlayerData
    _REPR_FIELDS = ("id", "name", "slug", "short_name", "full_name")

    @overload
    def __new__(cls, data: _TeamData, provider: SofascoreProvider, **kwargs) -> Team | Athlete: ...

    @overload
    def __new__(cls, data: _PlayerData, provider: SofascoreProvider, **kwargs) -> Athlete: ...

    def __new__(cls, data: _TeamData | _PlayerData, provider: SofascoreProvider, **kwargs):
        if cls is Competitor:
            cls = _competitor_class(data)
        return super().__new__(cls)

    @property
    def id(self) -> str:
        """The unique ID of the competitor."""
        return self.encode_id(self._data.id)

    @property
    def name(self) -> str:
        """The name of the competitor."""
        return self._data.name

    @property
    def slug(self) -> str:
        """The slug of the competitor."""
        return self._data.slug

    @property
    def short_name(self) -> str:
        """The short name of the competitor, falling back to the full name if unavailable."""
        return self._data.short_name or self._data.name

    @property
    @abstractmethod
    def full_name(self) -> str:
        """The full name of the competitor."""
        raise NotImplementedError("Subclasses must implement full_name property")

    @cached_property
    def gender(self) -> Gender | None:
        """The gender of the competitor."""
        from .enums import Gender
        return Gender(self._data.gender) if self._data.gender else None

    @property
    @abstractmethod
    def sport(self) -> Sport | None:
        """The sport this competitor belongs to, if available."""
        raise NotImplementedError("Subclasses must implement sport property")

    @cached_property
    def country(self) -> Country | None:
        """The country this competitor belongs to, if available."""
        from .core import Country
        return Country(self._data.country, self._provider) if self._data.country else None

    @classmethod
    def search(cls, query: str, provider: SofascoreProvider, max_results: int = 20) -> ScoredEntityCollection[Competitor]:
        """Search for competitors matching the given query, returning up to max_results results."""
        cls._validate_query(query)
        team_results = Team.search(query, provider, max_results)
        player_results = Athlete.search(query, provider, max_results)
        combined = ScoredEntityCollection.merge(team_results, player_results)
        return combined.sort_by_score()[:max_results]


class _TeamCompetitor(Competitor):
    """Private base for competitors backed by team-shaped payloads: `Team` and team-shaped
    athletes. Never instantiated as such."""
    _data: _TeamData

    def __init__(self, data: _TeamData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)
        if not isinstance(data, _TeamData):
            raise TypeError("Team competitor data must be of type _TeamData")

    @property
    def full_name(self) -> str:
        """The full name of the team."""
        return self._data.full_name or self._data.name

    @cached_property
    def sport(self) -> Sport:
        """The sport of the team."""
        from .core import Sport
        return Sport(self._data.sport, self._provider)

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Fetch all fixtures for this team competitor."""
        return self._fetch_paginated_events(self._provider.get_team_fixtures, self._data.id)

    def get_results(self, silent: bool = False) -> EventCollection:
        """Fetch all results for this team competitor."""
        return self._fetch_paginated_events(self._provider.get_team_results, self._data.id)

    @staticmethod
    def _fetch_entity(raw_id: int, provider: SofascoreProvider, **kwargs) -> _TeamData:
        try:
            return provider.get_team(raw_id).team
        except ProviderNotFoundError as e:
            logger.debug(f"Team with id {raw_id} not found: {e}")
            raise EntityNotFoundError(f"Team with id {raw_id} not found") from e
        except FetchError as e:
            logger.error(f"Network error while fetching team with id {raw_id}: {e}")
            raise DomainError(f"Network error while fetching team with id {raw_id}") from e


class _PlayerCompetitor(Competitor):
    """Private base for athletes backed by player-shaped payloads. Never instantiated as
    such."""
    _data: _PlayerData

    def __init__(self, data: _PlayerData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)
        if not isinstance(data, _PlayerData):
            raise TypeError("Player competitor data must be of type _PlayerData")

    @property
    def full_name(self) -> str:
        first = self._data.first_name or ""
        last = self._data.last_name or ""
        return f"{first} {last}".strip() or self._data.name

    @cached_property
    def sport(self) -> Sport | None:
        from .core import Sport
        return Sport(self._data.team.sport, self._provider) if self._data.team else None

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Fetch all fixtures for this player competitor."""
        if not silent:
            logger.warning(f"No fixtures endpoint for non individual sports players like {self.name}, returning empty collection")
        from .event import EventCollection
        return EventCollection()

    def get_results(self, silent: bool = False) -> EventCollection:
        """Fetch all results for this player competitor."""
        return self._fetch_paginated_events(self._provider.get_player_results, self._data.id)

    @staticmethod
    def _fetch_entity(raw_id: int, provider: SofascoreProvider, **kwargs) -> _PlayerData:
        try:
            return provider.get_player(raw_id)
        except ProviderNotFoundError as e:
            logger.debug(f"Player with id {raw_id} not found: {e}")
            raise EntityNotFoundError(f"Player with id {raw_id} not found") from e
        except FetchError as e:
            logger.error(f"Network error while fetching player with id {raw_id}: {e}")
            raise DomainError(f"Network error while fetching player with id {raw_id}") from e


class Team(_TeamCompetitor):
    """A club or national team, with its squad, manager and home venue.

    What a competitor is built as whenever its payload describes a team rather than one
    person — doubles pairs included. Everything `Competitor` offers is available here too;
    the members below are what `Team` adds.

    Attributes:
        name_code (str | None): Three-letter code, e.g. "PSG", "BAR".
        national (bool | None): Whether this is a national team, if the provider states it.
        players (EntityCollection[Athlete]): The squad — footballers, but equally the drivers
            of a motorsport team or the riders of a cycling team. Empty when the provider
            lists none.
        manager (Manager | None): The team's manager or head coach, if the provider names one.
        venue (Venue | None): The team's home ground, if the provider names one.
        id (str): Globally unique SDK ID, of the form "team:<id>". (inherited from Competitor)
        name, slug, short_name, full_name, gender, country, sport: See `Competitor`.
        source (_TeamData): The parsed payload backing this entity. (inherited from BaseEntity)

    Methods:
        search(query: str, provider: SofascoreProvider, max_results: int = 20) -> ScoredEntityCollection[Team]:
            Teams matching `query`, each with its relevance score, capped at `max_results`.
            (classmethod)
        get_fixtures(silent: bool = False) -> EventCollection: The team's upcoming events.
            (inherited from Competitor)
        get_results(silent: bool = False) -> EventCollection: The team's past events.
            (inherited from Competitor)
        get_events() -> EventCollection: Fixtures and results combined, sorted by start time.
            (inherited from EventAwareMixin)
        from_id(entity_id: str, provider: SofascoreProvider) -> Team: The team with this SDK ID.
            (classmethod, inherited from IdentifiableEntity)

    Raises:
        TypeError: If constructed with data that is not `_TeamData`.
        ValueError: If `search` is given an empty query, or if constructed from data that
            describes one person rather than a team.
        EntityNotFoundError: If `from_id` names a team the provider does not have.
        DomainError: If the provider fails with a network or transport error.
    """
    _data: _TeamData
    _PREFIX: str = "team"
    _REPR_FIELDS = ("id", "name", "slug", "short_name", "full_name", "name_code")

    def __init__(self, data: _TeamData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)
        if _is_individual(data):
            raise ValueError(f"Team data for '{data.name}' describes an athlete, not a team")

    @property
    def name_code(self) -> str | None:
        """The name code of the team, if available."""
        return self._data.name_code

    @property
    def national(self) -> bool | None:
        """Whether this team is a national team, if available."""
        return self._data.national

    @cached_property
    def players(self) -> EntityCollection[Athlete]:
        """
        The players of this team, if available and applicable.
        For motorsports teams, this will return the drivers, for cycling teams, the riders, etc.
        """
        return self._get_players() | self._get_drivers()

    def _get_players(self) -> EntityCollection[Athlete]:
        try:
            return EntityCollection([Athlete(player, self._provider) for player in self._provider.get_team_players(self._data.id).players])
        except ProviderNotFoundError:
            logger.debug(f"No players found for team with id {self.id}, returning empty collection")
            return EntityCollection()

    def _get_drivers(self) -> EntityCollection[Athlete]:
        try:
            return EntityCollection([Athlete(driver, self._provider) for driver in self._provider.get_team(self._data.id).drivers])
        except ProviderNotFoundError:
            logger.debug(f"No drivers found for team with id {self.id}, returning empty collection")
            return EntityCollection()

    @cached_property
    def manager(self) -> Manager | None:
        """The manager of this team, if available."""
        self._full_load()
        from .manager import Manager
        return Manager(self._data.manager, self._provider) if self._data.manager else None

    @cached_property
    def venue(self) -> Venue | None:
        """The venue this team plays at, if available."""
        self._full_load()
        from .venue import Venue
        return Venue(self._data.venue, self._provider) if self._data.venue else None

    @classmethod
    def search(cls, query: str, provider: SofascoreProvider, max_results: int = 20) -> ScoredEntityCollection[Team]:
        """Search for teams matching the given query, returning up to max_results results."""
        cls._validate_query(query)
        return cls._paginate_search(
            query=query,
            provider=provider,
            search_func=provider.search_teams,
            max_results=max_results
        )


class Athlete(Competitor):
    """An individual competitor — a footballer, a driver, a tennis player.

    What a competitor is built as whenever its payload describes one person. Everything
    `Competitor` offers is available here too; the members below are what `Athlete` adds.

    Instantiating `Athlete` returns one of two private variants depending on the payload:
    individual-sport athletes reach the provider as team-shaped records, team-sport players
    as player-shaped ones. Both expose the interface below.

    Attributes:
        first_name (str): Given name, parsed from the full name when not supplied separately.
        last_name (str): Family name, parsed from the full name when not supplied separately.
        parent (Team | None): The team, constructor or squad this athlete belongs to, if the
            provider names one.
        info (AthleteInfo | None): Physical, career and contractual details. Which fields are
            populated depends on the sport.
        id (str): Globally unique SDK ID — "t-ath:<id>" or "p-ath:<id>" by variant.
            (inherited from Competitor)
        name, slug, short_name, full_name, gender, country, sport: See `Competitor`.
        source (_TeamData | _PlayerData): The parsed payload backing this entity.
            (inherited from BaseEntity)

    Methods:
        search(query: str, provider: SofascoreProvider, max_results: int = 20) -> ScoredEntityCollection[Athlete]:
            Athletes matching `query`, each with its relevance score, capped at `max_results`.
            (classmethod)
        get_fixtures(silent: bool = False) -> EventCollection: The athlete's upcoming events.
            Always empty for a player-shaped athlete — the provider has no fixtures endpoint
            for players in team sports. (inherited from Competitor)
        get_results(silent: bool = False) -> EventCollection: The athlete's past events.
            (inherited from Competitor)
        get_events() -> EventCollection: Fixtures and results combined, sorted by start time.
            (inherited from EventAwareMixin)
        from_id(entity_id: str, provider: SofascoreProvider) -> Athlete: The athlete with this
            SDK ID. (classmethod, inherited from IdentifiableEntity)

    Raises:
        TypeError: If constructed with data that is neither `_PlayerData` nor `_TeamData`.
        ValueError: If `search` is given an empty query, or if constructed from team-shaped
            data that describes a team rather than one person.
        EntityNotFoundError: If `from_id` names an athlete the provider does not have.
        DomainError: If the provider fails with a network or transport error.
    """
    _data: _TeamData | _PlayerData
    _REPR_FIELDS = ("id", "name", "slug", "short_name", "full_name", "first_name", "last_name")

    @overload
    def __new__(cls, data: _PlayerData, provider: SofascoreProvider, **kwargs) -> _PlayerAthlete: ...

    @overload
    def __new__(cls, data: _TeamData, provider: SofascoreProvider, **kwargs) -> _TeamAthlete: ...

    def __new__(cls, data: _PlayerData | _TeamData, provider: SofascoreProvider, **kwargs):
        if cls is Athlete:
            if isinstance(data, _PlayerData):
                return super().__new__(_PlayerAthlete, data, provider, **kwargs)
            if isinstance(data, _TeamData):
                return super().__new__(_TeamAthlete, data, provider, **kwargs)
            raise TypeError("Athlete data must be either _PlayerData or _TeamData")
        return super().__new__(cls, data, provider, **kwargs)

    @property
    @abstractmethod
    def first_name(self) -> str:
        """The first name of the player."""
        raise NotImplementedError("Subclasses must implement first_name property")

    @property
    @abstractmethod
    def last_name(self) -> str:
        """The last name of the player."""
        raise NotImplementedError("Subclasses must implement last_name property")

    @property
    @abstractmethod
    def parent(self) -> Team | None:
        """The team this player belongs to, if available and applicable."""
        raise NotImplementedError("Subclasses must implement parent property")

    @property
    @abstractmethod
    def info(self) -> AthleteInfo | None:
        """Additional player info, if available."""
        raise NotImplementedError("Subclasses must implement info property")

    @classmethod
    def search(cls, query: str, provider: SofascoreProvider, max_results: int = 20) -> ScoredEntityCollection[Athlete]:
        """Search for players matching the given query, returning up to max_results results."""
        cls._validate_query(query)
        return cls._paginate_search(
            query=query,
            provider=provider,
            search_func=provider.search_player_team_persons,
            max_results=max_results
        )


class _TeamAthlete(Athlete, _TeamCompetitor):
    """Private `Athlete` variant backed by team-shaped payloads; see `Athlete`."""
    _data: _TeamData
    _PREFIX: str = "t-ath"

    def __init__(self, data: _TeamData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)
        if not _is_individual(data):
            raise ValueError(f"Team data for '{data.name}' describes a team, not an athlete")

    @property
    def first_name(self) -> str:
        """The first name of the player."""
        return self._get_human_name().first

    @property
    def last_name(self) -> str:
        """The last name of the player."""
        return self._get_human_name().last

    def _get_human_name(self) -> HumanName:
        return HumanName(self._data.full_name or self._data.name)

    @cached_property
    def parent(self) -> Team | None:
        """The team this athlete belongs to, if available and applicable."""
        self._full_load()
        return Team(self._data.parent_team, self._provider) if self._data.parent_team else None

    @cached_property
    def info(self) -> AthleteInfo | None:
        """Additional athlete info, if available."""
        self._full_load()
        if self._data.player_team_info is None:
            return None
        return AthleteInfo._from_parsed_player_team_info(self._data.player_team_info)


class _PlayerAthlete(Athlete, _PlayerCompetitor):
    """Private `Athlete` variant backed by player-shaped payloads; see `Athlete`."""
    _data: _PlayerData
    _PREFIX: str = "p-ath"

    @property
    def first_name(self) -> str:
        """The first name of the player."""
        return self._data.first_name or self._get_human_name().first

    @property
    def last_name(self) -> str:
        """The last name of the player."""
        return self._data.last_name or self._get_human_name().last

    def _get_human_name(self) -> HumanName:
        return HumanName(self._data.name)

    @cached_property
    def parent(self) -> Team | None:
        """The team this athlete belongs to, if available and applicable."""
        self._full_load()
        return Team(self._data.team, self._provider) if self._data.team else None

    @cached_property
    def info(self) -> AthleteInfo | None:
        """Additional athlete info, if available."""
        self._full_load()
        return AthleteInfo._from_parsed_player(self._data)


class AthleteInfo(DomainModel):
    """Physical, career and contractual details for an `Athlete`.

    Every field is optional and most are sport-specific: a footballer carries a preferred
    foot, positions and a market value, while a tennis player carries a birthplace and career
    prize money. Expect the majority to be None for any given athlete.

    Attributes:
        weight (float | None): Weight in kilograms.
        height (int | None): Height in centimetres.
        date_of_birth (date | None): Date of birth.
        place_of_birth (str | None): Birthplace, as a free-text string.
        retired (bool | None): Whether the athlete has retired.
        deceased (bool | None): Whether the athlete is deceased.
        number (int | None): Shirt, squad or car number.
        preferred_foot (str | None): Dominant foot, e.g. "Left", "Right", "Both".
        preferred_hand (str | None): Dominant hand, e.g. "right-handed".
        positions (list[str] | None): Positions played, most specific available, e.g. ["RW", "ST"].
        total_prizes (Amount | None): Career prize money, with its currency.
        salary (Amount | None): Current salary, with its currency.
        market_value (Amount | None): Estimated market value, with its currency.
        contract_expiry (date | None): When the athlete's current contract ends.
    """

    # --- Identity & Physical Attributes ---
    weight: float | None = None
    height: int | None = None
    date_of_birth: date | None = None
    place_of_birth: str | None = None
    retired: bool | None = None
    deceased: bool | None = None

    # --- Technical Profile & Gameplay ---
    number: int | None = None
    preferred_foot: str | None = None  # e.g. "left", "right", "both"
    preferred_hand: str | None = None  # e.g. "left", "right", "both"
    positions: list[str] | None = None

    # --- Valuation & Contractual Data ---
    total_prizes: Amount | None = None
    salary: Amount | None = None
    market_value: Amount | None = None
    contract_expiry: date | None = None

    @classmethod
    def _from_parsed_player_team_info(cls, data: _PlayerTeamInfoData) -> AthleteInfo:
        """Create a AthleteInfo instance from _PlayerTeamInfoData data."""
        return cls(
            weight=float(data.weight) if data.weight is not None else None,
            height=int(data.height * 100) if data.height is not None else None,
            date_of_birth=data.birth_date.date() if data.birth_date else None,
            place_of_birth=data.birthplace,
            number=int(data.number) if data.number is not None else None,
            preferred_hand=data.plays,
            total_prizes=data.prize_total,
        )

    @classmethod
    def _from_parsed_player(cls, data: _PlayerData) -> AthleteInfo:
        """Create a AthleteInfo instance from _PlayerData data."""
        return cls(
            weight=float(data.weight) if data.weight is not None else None,
            height=int(data.height) if data.height is not None else None,
            date_of_birth=data.date_of_birth.date() if data.date_of_birth else None,
            retired=data.retired,
            deceased=data.deceased,
            number=int(data.shirt_number) if data.shirt_number is not None else None,
            preferred_foot=data.preferred_foot,
            preferred_hand=data.preferred_hand,
            positions=(
                data.positions_detailed if data.positions_detailed is not None else
                [data.position] if data.position is not None else
                [data.primary_position] if data.primary_position is not None else
                None
            ),
            salary=data.salary,
            market_value=data.proposed_market_value,
            contract_expiry=data.contract_until.date() if data.contract_until else None,
        )
