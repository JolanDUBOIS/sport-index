from __future__ import annotations

from abc import abstractmethod
from datetime import date
from functools import cached_property
from pydantic import BaseModel
from typing import TYPE_CHECKING, Optional, Literal, Self, overload

from nameparser import HumanName

from . import logger
from .base import IdentifiableEntity, EntityCollection, SearchableMixin
from .event import Event, EventAwareMixin
from .types import CompetitorKind
from .utils import merge_pydantic_models
from sportindex.exceptions import ProviderNotFoundError, FetchError, EntityNotFoundError, DomainError
from sportindex.provider.models import _TeamData, _PlayerData

if TYPE_CHECKING:
    from .core import Category, Country, Sport
    from .enums import Gender
    from .event import EventCollection
    from .manager import Manager
    from .venue import Venue
    from sportindex.provider import SofascoreProvider
    from sportindex.provider.models import BaseSchema, _PlayerTeamInfoData, Amount


class Competitor(IdentifiableEntity, EventAwareMixin[Event], SearchableMixin):
    """A sports competitor, either an individual or a team.

    Provides access to identity, affiliations, and related entities such as players, managers, and venues.
    Supports fetching fixtures and results, and distinguishing between player and team competitors.

    Attributes:
        id (int): Unique competitor ID.
        name (str): Official competitor name.
        slug (str): URL-friendly slug.
        short_name (str): Abbreviated name.
        gender (Gender | None): Competitor gender, if applicable.
        country (Country | None): Competitor's country, if available.

    Abstract Properties:
        full_name (str): Full name or concatenation of first and last names for players.
        kind (Literal["player", "team"]): "player" or "team", indicating the type of competitor.
        sport (Sport | None): Sport this competitor belongs to.
        category (Category | None): Competitor's category, if available.

    Methods:
        get_fixtures(silent=False) -> EventCollection: Fetch all scheduled events for the competitor.
        get_results(silent=False) -> EventCollection: Fetch all results for the competitor.

    Raises:
        TypeError: If initialized with invalid data type.
        EntityNotFoundError: If the competitor does not exist in the provider.
        DomainError: If a network or provider error occurs during fetch.
    """
    _data: _TeamData | _PlayerData
    _REPR_FIELDS = ("id", "name", "slug", "short_name", "full_name")
    _TYPE_MAP: dict[type[BaseSchema], int] = {_TeamData: 1, _PlayerData: 2}
    _REVERSE_TYPE_MAP: dict[int, type[BaseSchema]] = {1: _TeamData, 2: _PlayerData}

    @overload
    def __new__(cls, data: _PlayerData, provider: SofascoreProvider, **kwargs) -> Player: ...

    def __new__(cls, data: _TeamData | _PlayerData, provider: SofascoreProvider, **kwargs):
        if cls is Competitor:
            if isinstance(data, _PlayerData) or (isinstance(data, _TeamData) and data.player_team_info is not None):
                return super().__new__(Player)
            elif isinstance(data, _TeamData):
                return super().__new__(Team)
            else:
                raise TypeError("Competitor data must be either _TeamData or _PlayerData")
        else:
            return super().__new__(cls)

    def __init__(self, data: _TeamData | _PlayerData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, (_TeamData, _PlayerData)):
            raise TypeError("Competitor data must be either _TeamData or _PlayerData")

        self._full_loaded = False

    @property
    def id(self) -> int:
        """The unique ID of the competitor."""
        type_idx = self._TYPE_MAP[type(self._data)]
        return self.encode_id(self._data.id, type_idx)

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
        raise NotImplementedError("Property full_name must be implemented in subclasses")

    @property
    @abstractmethod
    def kind(self) -> CompetitorKind:
        """The kind of competitor, either 'player' or 'team'."""
        raise NotImplementedError("Property kind must be implemented in subclasses")

    @cached_property
    def gender(self) -> Optional[Gender]:
        """The gender of the competitor."""
        from .enums import Gender
        return Gender(self._data.gender) if self._data.gender else None

    @property
    @abstractmethod
    def sport(self) -> Optional[Sport]:
        """The sport this competitor belongs to."""
        raise NotImplementedError("Property sport must be implemented in subclasses")

    @cached_property
    def country(self) -> Optional[Country]:
        """The country this competitor belongs to, if available."""
        from .core import Country
        return Country(self._data.country, self._provider) if self._data.country else None

    @property
    @abstractmethod
    def category(self) -> Optional[Category]:
        """The category this competitor belongs to, if available."""
        raise NotImplementedError("Property category must be implemented in subclasses")

    def get_fixtures(self, silent: bool = False) -> EventCollection[Event]:
        """Fetch all fixtures for this competitor."""
        from .event import EventCollection
        if isinstance(self._data, _PlayerData):
            if not silent:
                logger.warning(f"No fixtures endpoint for non individual sports players like {self.name}, returning empty collection")
            # NOTE - Should we raise ProviderNotFoundError or similar instead ?
            return EventCollection([])
        elif isinstance(self._data, _TeamData):
            return self._fetch_paginated_events(self._provider.get_team_fixtures, self._data.id)
        return EventCollection([])

    def get_results(self, silent: bool = False) -> EventCollection[Event]:
        """Fetch all results for this competitor."""
        if isinstance(self._data, _PlayerData):
            return self._fetch_paginated_events(self._provider.get_player_results, self._data.id)
        elif isinstance(self._data, _TeamData):
            return self._fetch_paginated_events(self._provider.get_team_results, self._data.id)
        from .event import EventCollection
        return EventCollection([])

    def _full_load(self) -> None:
        """
        Lazy-loads the complete competitor from the provider.
        Called automatically when accessing properties that require full details
        missing from the initial lightweight API response.
        """
        if self._full_loaded:
            return

        self._data = merge_pydantic_models(self._data, self._fetch_entity(self._data.id, self._provider, type(self._data), strict=False))

        self._full_loaded = True
        self._clear_cache()

    @classmethod
    def from_id(cls, competitor_id: int, provider: SofascoreProvider) -> Self:
        """Fetch a competitor by its ID."""
        raw_id, type_idx = cls.decode_id(competitor_id)

        if type_idx not in cls._REVERSE_TYPE_MAP:
            raise TypeError(f"Invalid competitor ID {competitor_id}: unknown type index {type_idx}")

        data_cls = cls._REVERSE_TYPE_MAP[type_idx]
        entity_data = cls._fetch_entity(raw_id, provider, data_cls)

        instance = cls(entity_data, provider)
        if not issubclass(type(instance), cls):
            raise TypeError(
                f"ID {competitor_id} belongs to a {type(instance).__name__}, but was initialized as a {cls.__name__}. "
                f"Use {type(instance).__name__}.from_id() instead."
            )

        return instance

    @classmethod
    @abstractmethod
    def search(cls, query: str, provider: SofascoreProvider, max_results: int = 20) -> EntityCollection[Competitor]:
        """Search for competitors matching the given query, returning up to max_results results."""
        raise NotImplementedError("Method search must be implemented in subclasses")

    @overload
    @classmethod
    def _fetch_entity(cls, entity_id: int, provider: SofascoreProvider, data_cls: type[_TeamData | _PlayerData], strict: Literal[True] = True) -> _TeamData | _PlayerData: ...

    @overload
    @classmethod
    def _fetch_entity(cls, entity_id: int, provider: SofascoreProvider, data_cls: type[_TeamData | _PlayerData], strict: Literal[False]) -> Optional[_TeamData | _PlayerData]: ...

    @classmethod
    def _fetch_entity(cls, entity_id: int, provider: SofascoreProvider, data_cls: type[_TeamData | _PlayerData], strict: bool = True) -> Optional[_TeamData | _PlayerData]:
        """Fetch the complete event data from the provider by its raw ID and data class."""
        try:
            if data_cls == _TeamData:
                return cls._fetch_td(entity_id, provider)
            elif data_cls == _PlayerData:
                return cls._fetch_pd(entity_id, provider)
            else:
                raise TypeError(f"Unsupported data class {data_cls} for competitor entity fetch")
        except ProviderNotFoundError:
            logger.debug(f"Competitor entity with id {entity_id} and data class {data_cls} not found during fetch")
            if strict:
                raise EntityNotFoundError(f"Competitor entity with id {entity_id} not found") from None
        except FetchError as e:
            logger.debug(f"Network error while fetching competitor entity with id {entity_id} and data class {data_cls}: {e}")
            if strict:
                raise DomainError(f"Network error while fetching competitor entity with id {entity_id}") from e
        return None

    @staticmethod
    def _fetch_td(raw_id: int, provider: SofascoreProvider) -> _TeamData:
        """Fetch a team by its ID."""
        return provider.get_team(raw_id).team

    @staticmethod
    def _fetch_pd(raw_id: int, provider: SofascoreProvider) -> _PlayerData:
        """Fetch a player by its ID."""
        return provider.get_player(raw_id)


class Team(Competitor):
    """
    A sports team competitor, which may have associated players, a manager, and a home venue.
    
    Attributes:
        name_code (str | None): The name code of the team, if available.
        national (bool | None): Whether this team is a national team, if available.
        players (EntityCollection[Player]): The players of this team, if available and applicable.
        manager (Manager | None): The manager of this team, if available.
        venue (Venue | None): The venue this team plays at, if available.
    """
    _data: _TeamData
    _REPR_FIELDS = ("id", "name", "slug", "short_name", "full_name", "name_code", "kind")

    def __init__(self, data: _TeamData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _TeamData):
            raise TypeError("Team data must be of type _TeamData")
        if data.player_team_info is not None:
            raise TypeError("Team data with player_team_info should be represented as a Player, not a Team")

    @property
    def full_name(self) -> str:
        """The full name of the team."""
        return self._data.full_name or self._data.name

    @property
    def name_code(self) -> Optional[str]:
        """The name code of the team, if available."""
        return self._data.name_code

    @property
    def kind(self) -> Literal["team"]:
        """The kind of competitor, which is 'team' for this class."""
        return "team"

    @property
    def national(self) -> Optional[bool]:
        """Whether this team is a national team, if available."""
        return self._data.national

    @cached_property
    def sport(self) -> Sport:
        """The sport this team belongs to."""
        from .core import Sport
        return Sport(self._data.sport, self._provider)

    @cached_property
    def category(self) -> Optional[Category]:
        """The category this team belongs to, if available."""
        from .core import Category
        return Category(self._data.category, self._provider) if self._data.category else None

    @cached_property
    def players(self) -> EntityCollection[Player]:
        """
        The players of this team, if available and applicable.
        For motorsports teams, this will return the drivers, for cycling teams, the riders, etc. 
        """
        return self._get_players() | self._get_drivers()

    def _get_players(self) -> EntityCollection[Player]:
        try:
            return EntityCollection([Player(player, self._provider) for player in self._provider.get_team_players(self._data.id).players])
        except ProviderNotFoundError:
            logger.debug(f"No players found for team with id {self.id}, returning empty collection")
            return EntityCollection([])

    def _get_drivers(self) -> EntityCollection[Player]:
        try:
            return EntityCollection([Player(driver, self._provider) for driver in self._provider.get_team(self._data.id).drivers])
        except ProviderNotFoundError:
            logger.debug(f"No drivers found for team with id {self.id}, returning empty collection")
            return EntityCollection([])

    @cached_property
    def manager(self) -> Optional[Manager]:
        """The manager of this team, if available."""
        self._full_load()
        from .manager import Manager
        return Manager(self._data.manager, self._provider) if self._data.manager else None

    @cached_property
    def venue(self) -> Optional[Venue]:
        """The venue this team plays at, if available."""
        self._full_load()
        from .venue import Venue
        return Venue(self._data.venue, self._provider) if self._data.venue else None

    @classmethod
    def search(cls, query: str, provider: SofascoreProvider, max_results: int = 20) -> EntityCollection[Team]:
        """Search for teams matching the given query, returning up to max_results results."""
        return cls._paginate_search(
            query=query,
            provider=provider,
            search_func=provider.search_teams,
            max_results=max_results
        )


class Player(Competitor):
    """
    A player competitor, associated with a team and potentially having detailed information.
    
    Attributes:
        first_name (str | None): The first name of the player, if available.
        last_name (str | None): The last name of the player, if available.
        parent (Team | None): The team this player belongs to, if available and applicable.
        info (PlayerInfo | None): Additional player info, if available.
    """
    _data: _TeamData | _PlayerData
    _REPR_FIELDS = ("id", "name", "slug", "short_name", "full_name", "first_name", "last_name", "kind")

    def __init__(self, data: _TeamData | _PlayerData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if isinstance(data, _TeamData) and data.player_team_info is None:
            raise TypeError("Team data without player_team_info should be represented as a Team, not a Player")

    @property
    def full_name(self) -> str:
        """The full name of the player."""
        if isinstance(self._data, _TeamData):
            return self._data.full_name or self._data.name
        elif isinstance(self._data, _PlayerData):
            first = self._data.first_name or ""
            last = self._data.last_name or ""
            return f"{first} {last}".strip() or self._data.name

    @property
    def first_name(self) -> Optional[str]:
        """The first name of the player, if available."""
        if isinstance(self._data, _PlayerData):
            return self._data.first_name
        elif isinstance(self._data, _TeamData):
            name = HumanName(self._data.full_name or self._data.name)
            return name.first

    @property
    def last_name(self) -> Optional[str]:
        """The last name of the player, if available."""
        if isinstance(self._data, _PlayerData):
            return self._data.last_name
        elif isinstance(self._data, _TeamData):
            name = HumanName(self._data.full_name or self._data.name)
            return name.last

    @property
    def kind(self) -> Literal["player"]:
        """The kind of competitor, which is 'player' for this class."""
        return "player"

    @cached_property
    def sport(self) -> Sport:
        """The sport this player belongs to."""
        from .core import Sport
        if isinstance(self._data, _PlayerData):
            return Sport(self._data.team.sport, self._provider)
        elif isinstance(self._data, _TeamData):
            return Sport(self._data.sport, self._provider)

    @cached_property
    def category(self) -> Optional[Category]:
        """The category this player belongs to, if available."""
        from .core import Category
        if isinstance(self._data, _PlayerData):
            return Category(self._data.team.category, self._provider) if self._data.team and self._data.team.category else None
        elif isinstance(self._data, _TeamData):
            return Category(self._data.category, self._provider) if self._data.category else None

    @cached_property
    def parent(self) -> Optional[Team]:
        """The team this player belongs to, if available and applicable."""
        self._full_load()
        if isinstance(self._data, _PlayerData):
            return Team(self._data.team, self._provider) if self._data.team else None
        elif isinstance(self._data, _TeamData):
            return Team(self._data.parent_team, self._provider) if self._data.parent_team else None

    @cached_property
    def info(self) -> Optional[PlayerInfo]:
        """Additional player info, if available."""
        self._full_load()
        if isinstance(self._data, _PlayerData):
            return PlayerInfo._from_parsed_player(self._data)
        elif isinstance(self._data, _TeamData) and self._data.player_team_info is not None:
            return PlayerInfo._from_parsed_player_team_info(self._data.player_team_info)

    @classmethod
    def search(cls, query: str, provider: SofascoreProvider, max_results: int = 20) -> EntityCollection[Player]:
        """Search for players matching the given query, returning up to max_results results."""
        return cls._paginate_search(
            query=query,
            provider=provider,
            search_func=provider.search_player_team_persons,
            max_results=max_results
        )


class PlayerInfo(BaseModel):
    """Comprehensive details about an individual athlete.

    Covers identity, physical attributes, career status, technical profile, and financial/contractual data.

    Attributes:
        weight (float | None): Player weight in kilograms.
        height (int | None): Player height in centimeters.
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
    weight: Optional[float] = None
    height: Optional[int] = None
    date_of_birth: Optional[date] = None
    place_of_birth: Optional[str] = None
    retired: Optional[bool] = None
    deceased: Optional[bool] = None

    # --- Technical Profile & Gameplay ---
    number: Optional[int] = None
    preferred_foot: Optional[str] = None  # e.g. "left", "right", "both"
    preferred_hand: Optional[str] = None  # e.g. "left", "right", "both"
    positions: Optional[list[str]] = None

    # --- Valuation & Contractual Data ---
    total_prizes: Optional[Amount] = None
    salary: Optional[Amount] = None
    market_value: Optional[Amount] = None
    contract_expiry: Optional[date] = None

    @classmethod
    def _from_parsed_player_team_info(cls, data: _PlayerTeamInfoData) -> PlayerInfo:
        """Create a PlayerInfo instance from _PlayerTeamInfoData data."""
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
    def _from_parsed_player(cls, data: _PlayerData) -> PlayerInfo:
        """Create a PlayerInfo instance from _PlayerData data."""
        return cls(
            weight=float(data.weight) if data.weight is not None else None,
            height=int(data.height) if data.height is not None else None,
            date_of_birth=data.date_of_birth.date() if data.date_of_birth else None,
            retired=data.retired,
            deceased=data.deceased,
            number=int(data.shirt_number) if data.shirt_number is not None else None,
            preferred_foot=data.preferred_foot,
            preferred_hand=data.preferred_hand,
            positions=data.positions_detailed or [data.position] or [data.primary_position] or None,
            salary=data.salary,
            market_value=data.proposed_market_value,
            contract_expiry=data.contract_until.date() if data.contract_until else None,
        )
