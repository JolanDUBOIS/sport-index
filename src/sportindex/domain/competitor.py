from __future__ import annotations

import logging
from abc import abstractmethod
from datetime import date  # noqa: TC003
from functools import cached_property
from typing import TYPE_CHECKING, overload

from nameparser import HumanName
from pydantic import BaseModel

from sportindex.api_client.models import Amount, _PlayerData, _TeamData
from sportindex.exceptions import (
    DomainError,
    EntityNotFoundError,
    FetchError,
    ProviderNotFoundError,
)

from .base import SearchableMixin
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


class Competitor(SearchableMixin, EventAwareMixin):
    """A sports competitor, either an individual or a team.

    Provides access to identity, affiliations, and related entities such as players, managers, and venues.
    Supports fetching fixtures and results, and distinguishing between player and team competitors.

    Attributes:
        id (str): Unique competitor ID.
        name (str): Official competitor name.
        slug (str): URL-friendly slug.
        short_name (str): Abbreviated name.
        gender (Gender | None): Competitor gender, if applicable.
        country (Country | None): Competitor's country, if available.
        full_name (str): Full name or concatenation of first and last names for players.
        sport (Sport | None): Sport this competitor belongs to.

    Methods:
        get_fixtures(silent=False) -> EventCollection: Fetch all scheduled events for the competitor.
        get_results(silent=False) -> EventCollection: Fetch all results for the competitor.
        search(query, provider, max_results) -> ScoredEntityCollection: Search for competitors matching a query string.

    Raises:
        TypeError: If initialized with invalid data type.
        EntityNotFoundError: If the competitor does not exist in the provider.
        DomainError: If a network or provider error occurs during fetch.
    """
    _data: _TeamData | _PlayerData
    _REPR_FIELDS = ("id", "name", "slug", "short_name", "full_name")

    @overload
    def __new__(cls, data: _TeamData, provider: SofascoreProvider, **kwargs) -> _TeamCompetitor: ...

    @overload
    def __new__(cls, data: _PlayerData, provider: SofascoreProvider, **kwargs) -> _PlayerCompetitor: ...

    def __new__(cls, data: _TeamData | _PlayerData, provider: SofascoreProvider, **kwargs):
        if cls is Competitor:
            if isinstance(data, _TeamData):
                return super().__new__(_TeamCompetitor)
            if isinstance(data, _PlayerData):
                return super().__new__(_PlayerCompetitor)
            raise TypeError(f"Competitor data must be either _TeamData or _PlayerData, got {type(data)}")
        return super().__new__(cls)

    def __init__(self, data: _TeamData | _PlayerData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)
        self._resolved_instance: Team | Athlete | None = None

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
        """The short name of the competitor."""
        return self._data.short_name

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
    def sport(self) -> Sport:
        """The sport this competitor belongs to."""
        raise NotImplementedError("Subclasses must implement sport property")

    @cached_property
    def country(self) -> Country | None:
        """The country this competitor belongs to, if available."""
        from .core import Country
        return Country(self._data.country, self._provider) if self._data.country else None

    @abstractmethod
    def resolve(self) -> Team | Athlete:
        """Resolve this competitor to its specific type (Team or Athlete)."""
        raise NotImplementedError("Subclasses must implement resolve method")

    @classmethod
    def search(cls, query: str, provider: SofascoreProvider, max_results: int = 20) -> ScoredEntityCollection[Competitor]:
        """Search for competitors matching the given query, returning up to max_results results."""
        cls._validate_query(query)
        team_results = Team.search(query, provider, max_results)
        player_results = Athlete.search(query, provider, max_results)
        combined = ScoredEntityCollection.merge(team_results, player_results)
        return combined.sort_by_score()[:max_results]


class _TeamCompetitor(Competitor):
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

    def resolve(self) -> Team | Athlete:
        """Resolve this competitor to its specific type (Team or Athlete)."""
        if self._resolved_instance is not None:
            return self._resolved_instance

        self._full_load()
        if self._data.player_team_info is not None:
            self._resolved_instance = Athlete(self._data, self._provider)
        else:
            self._resolved_instance = Team(self._data, self._provider)
        return self._resolved_instance

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
    def sport(self) -> Sport:
        from .core import Sport
        return Sport(self._data.team.sport, self._provider)

    def resolve(self) -> Athlete:
        """Resolve this competitor to its specific type (Team or Athlete). In this case, it will always be an Athlete."""
        if self._resolved_instance is None:
            self._resolved_instance = Athlete(self._data, self._provider)
        return self._resolved_instance

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
    """
    A sports team competitor, which may have associated players, a manager, and a home venue.

    Attributes:
        name_code (str | None): The name code of the team, if available.
        national (bool | None): Whether this team is a national team, if available.
        players (EntityCollection[Athlete]): The players of this team, if available and applicable.
        manager (Manager | None): The manager of this team, if available.
        venue (Venue | None): The venue this team plays at, if available.
    """
    _data: _TeamData
    _PREFIX: str = "team"
    _REPR_FIELDS = ("id", "name", "slug", "short_name", "full_name", "name_code")

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

    def resolve(self) -> Team:
        """Resolve this competitor to its specific type (Team or Athlete). In this case, it will always be a Team."""
        return self

    @classmethod
    def search(cls, query: str, provider: SofascoreProvider, max_results: int = 20) -> ScoredEntityCollection[Team]:
        """Search for teams matching the given query, returning up to max_results results."""
        return cls._paginate_search(
            query=query,
            provider=provider,
            search_func=provider.search_teams,
            max_results=max_results
        )


class Athlete(Competitor):
    """
    A player competitor, associated with a team and potentially having detailed information.

    Attributes:
        first_name (str | None): The first name of the player, if available.
        last_name (str | None): The last name of the player, if available.
        parent (Team | None): The team this player belongs to, if available and applicable.
        info (AthleteInfo | None): Additional player info, if available.
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
                return super().__new__(_PlayerAthlete)
            if isinstance(data, _TeamData):
                return super().__new__(_TeamAthlete)
            raise TypeError("Athlete data must be either _PlayerData or _TeamData")
        return super().__new__(cls)

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

    def resolve(self) -> Athlete:
        """Resolve this competitor to its specific type (Team or Athlete). In this case, it will always be an Athlete."""
        return self

    @classmethod
    def search(cls, query: str, provider: SofascoreProvider, max_results: int = 20) -> ScoredEntityCollection[Athlete]:
        """Search for players matching the given query, returning up to max_results results."""
        return cls._paginate_search(
            query=query,
            provider=provider,
            search_func=provider.search_player_team_persons,
            max_results=max_results
        )


class _TeamAthlete(Athlete, _TeamCompetitor):
    _data: _TeamData
    _PREFIX: str = "t-ath"

    def __init__(self, data: _TeamData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)
        if data.player_team_info is None:
            raise ValueError("Team data without player_team_info cannot be represented as a TeamAthlete")

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
        return AthleteInfo._from_parsed_player_team_info(self._data.player_team_info)


class _PlayerAthlete(Athlete, _PlayerCompetitor):
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


class AthleteInfo(BaseModel):
    """Comprehensive details about an individual athlete.

    Covers identity, physical attributes, career status, technical profile, and financial/contractual data.

    Attributes:
        weight (float | None): Athlete weight in kilograms.
        height (int | None): Athlete height in centimeters.
        date_of_birth (date | None): Birth date.
        place_of_birth (str | None): Birthplace.
        retired (bool | None): Whether the player is retired.
        deceased (bool | None): Whether the player is deceased.
        number (int | None): Shirt or squad number.
        preferred_foot (str | None): Dominant foot (if applicable).
        preferred_hand (str | None): Dominant hand (if applicable).
        positions (list[str] | None): Positions played.
        total_prizes (Amount | None): Career prize earnings.
        salary (Amount | None): Current salary.
        market_value (Amount | None): Market valuation.
        contract_expiry (date | None): Contract end date.
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
