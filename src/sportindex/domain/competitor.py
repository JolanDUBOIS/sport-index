from __future__ import annotations

from functools import cached_property
from datetime import date
from pydantic import BaseModel
from typing import TYPE_CHECKING, Optional, Literal

from . import logger
from .base import IdentifiableEntity, EventAwareMixin, EntityCollection
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
    from sportindex.provider.models import _PlayerTeamInfoData, Amount


class Competitor(IdentifiableEntity[_TeamData | _PlayerData], EventAwareMixin):
    """A sports competitor, either an individual or a team.

    Provides access to identity, affiliations, and related entities such as players, managers, and venues.
    Supports fetching fixtures and results, and distinguishing between player and team competitors.

    Attributes:
        id (int): Unique competitor ID.
        name (str): Official competitor name.
        slug (str): URL-friendly slug.
        short_name (str): Abbreviated name.
        full_name (str): Full name or concatenation of first and last names for players.
        kind (Literal['team','player']): Type of competitor.
        sport (Sport | None): Sport this competitor belongs to.
        country (Country | None): Competitor's country, if applicable.
        category (Category | None): Competitor's category, if applicable.
        manager (Manager | None): Manager, if applicable.
        venue (Venue | None): Home venue, if applicable.
        players (EntityCollection[Competitor] | None): Players of this team, if applicable.
        parent (Competitor | None): Parent competitor for players or sub-teams.
        player_info (PlayerInfo | None): Detailed player information, if applicable.

    Methods:
        get_fixtures(silent=False) -> EventCollection: Fetch all scheduled events for the competitor.
        get_results(silent=False) -> EventCollection: Fetch all results for the competitor.

    Raises:
        TypeError: If initialized with invalid data type.
        EntityNotFoundError: If the competitor does not exist in the provider.
        DomainError: If a network or provider error occurs during fetch.
    """
    _REPR_FIELDS = ("id", "name", "slug", "short_name", "full_name", "name_code", "national", "gender", "sport", "country", "category", "kind")
    _TYPE_MAP = {_TeamData: 1, _PlayerData: 2}

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
        return self._data.shortName

    @property
    def full_name(self) -> str:
        """The full name of the competitor."""
        if isinstance(self._data, _TeamData):
            return self._data.fullName or self._data.name
        elif isinstance(self._data, _PlayerData):
            first = self._data.firstName or ""
            last = self._data.lastName or ""
            return f"{first} {last}".strip() or self._data.name

    @property
    def name_code(self) -> Optional[str]:
        """The name code of the competitor, if applicable."""
        if isinstance(self._data, _TeamData):
            return self._data.nameCode
        else:
            return None

    @property
    def national(self) -> Optional[bool]:
        """Whether this competitor is a national team."""
        if isinstance(self._data, _TeamData):
            return self._data.national
        else:
            return None

    # --- Properties to be cached, as they require additional API calls or processing (even if they are quite light) ---

    @cached_property
    def gender(self) -> Optional[Gender]:
        """The gender of the competitor, if applicable."""
        from .enums import Gender
        return Gender(self._data.gender)

    @cached_property
    def sport(self) -> Optional[Sport]:
        """The sport this competitor belongs to."""
        from .core import Sport
        if isinstance(self._data, _TeamData):
            return Sport(self._data.sport, self._provider) if self._data.sport else None
        elif isinstance(self._data, _PlayerData):
            return Sport(self._data.team.sport, self._provider) if self._data.team and self._data.team.sport else None

    @cached_property
    def country(self) -> Optional[Country]:
        """The country this competitor belongs to, if applicable."""
        from .core import Country
        return Country(self._data.country, self._provider) if self._data.country else None

    @cached_property
    def category(self) -> Optional[Category]:
        """The category this competitor belongs to, if applicable."""
        from .core import Category
        if isinstance(self._data, _TeamData):
            return Category(self._data.category, self._provider) if self._data.category else None
        elif isinstance(self._data, _PlayerData):
            return Category(self._data.team.category, self._provider) if self._data.team and self._data.team.category else None

    @cached_property
    def kind(self) -> Literal["team", "player"]:
        """Whether this competitor is a team or a player."""
        if isinstance(self._data, _PlayerData):
            return "player"
        elif isinstance(self._data, _TeamData):
            if self._data.playerTeamInfo is not None:
                logger.debug(f"Team {self._data.name} has playerTeamInfo, treating it as a player")
                return "player"
            else:
                return "team"

    @cached_property
    def parent(self) -> Optional[Competitor]:
        """The parent competitor, if this is a player belonging to a team."""
        self._full_load()
        if isinstance(self._data, _PlayerData) and self._data.team is not None:
            return Competitor(self._data.team, self._provider)
        elif isinstance(self._data, _TeamData) and self._data.parent_team is not None:
            return Competitor(self._data.parent_team, self._provider)
        else:
            return None

    @cached_property
    def players(self) -> Optional[EntityCollection[Competitor]]:
        """The players belonging to this competitor, if this is a team."""
        if not isinstance(self._data, _TeamData):
            return None
        try:
            return EntityCollection([Competitor(player, self._provider) for player in self._provider.get_team_players(self._data.id).players])
        except ProviderNotFoundError:
            logger.debug(f"No players found for team with id {self.id}, returning empty collection")
            return EntityCollection([])

    @cached_property
    def drivers(self) -> Optional[EntityCollection[Competitor]]:
        """The drivers belonging to this competitor, if this is a motorsport team."""
        if not isinstance(self._data, _TeamData):
            return None
        try:
            return EntityCollection([Competitor(driver, self._provider) for driver in self._provider.get_team(self._data.id).drivers])
        except ProviderNotFoundError:
            logger.debug(f"No drivers found for team with id {self.id}, returning empty collection")
            return EntityCollection([])

    @cached_property
    def manager(self) -> Optional[Manager]:
        """The manager of this competitor, if applicable."""
        self._full_load()
        from .manager import Manager
        return Manager(self._data.manager, self._provider) if self._data.manager else None

    @cached_property
    def venue(self) -> Optional[Venue]:
        """The venue this competitor plays at, if applicable."""
        self._full_load()
        from .venue import Venue
        return Venue(self._data.venue, self._provider) if self._data.venue else None

    @cached_property
    def player_info(self) -> Optional[PlayerInfo]:
        """Additional player info, if this is a player."""
        if self.kind != "player":
            return None
        self._full_load()
        if isinstance(self._data, _PlayerData):
            return PlayerInfo._from_parsed_player(self._data)
        elif isinstance(self._data, _TeamData) and self._data.player_team_info is not None:
            return PlayerInfo._from_parsed_player_team_info(self._data.player_team_info)
        else:
            return None

    # --- Properties to be recomputed each time, as they might change regularly ---

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Fetch all fixtures for this competitor."""
        if isinstance(self._data, _PlayerData):
            if not silent:
                logger.warning(f"No fixtures endpoint for non individual sports players like {self.name}, returning empty list")
            from .event import EventCollection
            return EventCollection([])
        elif isinstance(self._data, _TeamData):
            return self._fetch_paginated_events(self._provider.get_team_fixtures, self._data.id)
        from .event import EventCollection
        return EventCollection([])

    def get_results(self, silent: bool = False) -> EventCollection:
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
        try:
            if isinstance(self._data, _PlayerData):
                self._data = merge_pydantic_models(self._data, self._provider.get_player(self._data.id))
            elif isinstance(self._data, _TeamData):
                self._data = merge_pydantic_models(self._data, self._provider.get_team(self._data.id))
            if not isinstance(self._data, (_PlayerData, _TeamData)):
                raise TypeError("Competitor data must be either _PlayerData or _TeamData.")
            self._full_loaded = True
        except ProviderNotFoundError:
            logger.debug(f"Competitor with id {self._data.id} not found during full load.")
            self._full_loaded = True
        except FetchError as e:
            logger.debug(f"Network error while fully loading competitor with id {self._data.id}: {e}")
            self._full_loaded = True
        self._clear_cache()

    @classmethod
    def from_id(cls, competitor_id: int, provider: SofascoreProvider) -> Competitor:
        """Fetch a competitor by its ID."""
        raw_id, type_idx = cls.decode_id(competitor_id)
        type_map_reverse = {v: k for k, v in cls._TYPE_MAP.items()}

        if type_idx not in type_map_reverse:
            raise TypeError(f"Invalid competitor ID {competitor_id}: unknown type index {type_idx}")

        data_cls = type_map_reverse[type_idx]
        try:
            if data_cls == _TeamData:
                parsed_data = provider.get_team(raw_id).team
            elif data_cls == _PlayerData:
                parsed_data = provider.get_player(raw_id)
            else:
                raise TypeError(f"Unsupported competitor type index {type_idx} in ID {competitor_id}")
        except ProviderNotFoundError as e:
            raise EntityNotFoundError(f"Competitor with id {competitor_id} not found") from e
        except FetchError as e:
            raise DomainError(f"Network error while fetching competitor {competitor_id}") from e

        return cls(parsed_data, provider)

    @classmethod
    def search(cls, query: str, provider: SofascoreProvider) -> EntityCollection[Competitor]:
        """Search for competitors matching the given query (up to the first 20 matches)."""
        entities = []
        for page in range(51):
            try:
                all_matches = provider.search_all(query=query, page=page)
            except (ProviderNotFoundError, FetchError):
                logger.debug(f"Failed to fetch search results for query '{query}' on page {page}, stopping pagination")
                break
            if not all_matches:
                break
            for item in all_matches:
                if isinstance(item.entity, (_TeamData, _PlayerData)):
                    entities.append(Competitor(item.entity, provider))
            if len(all_matches) > 20:
                break
        return EntityCollection(entities[:20])


class PlayerInfo(BaseModel):
    """Comprehensive details about an individual athlete.

    Covers identity, physical attributes, career status, technical profile, and financial/contractual data.

    Attributes:
        first_name (str | None): Player's first name.
        last_name (str | None): Player's last name.
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

    Methods:
        _from_parsed_player(data: _PlayerData) -> PlayerInfo: Create instance from _PlayerData data.
        _from_parsed_player_team_info(data: _PlayerTeamInfoData) -> PlayerInfo: Create instance from _PlayerTeamInfoData data.
    """

    # --- Identity & Physical Attributes ---
    first_name: Optional[str] = None
    last_name: Optional[str] = None
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
            weight=float(data.weight),
            height=int(data.height * 100),
            date_of_birth=data.birth_date.date() if data.birth_date else None,
            place_of_birth=data.birthplace,
            number=int(data.number),
            preferred_foot=data.plays, # Note: probably never populated, as there are not single sport using the foot preference field...
            preferred_hand=data.plays,
            total_prizes=data.prize_total,
        )

    @classmethod
    def _from_parsed_player(cls, data: _PlayerData) -> PlayerInfo:
        """Create a PlayerInfo instance from _PlayerData data."""
        return cls(
            first_name=data.first_name,
            last_name=data.last_name,
            weight=float(data.weight),
            height=int(data.height),
            date_of_birth=data.date_of_birth.date() if data.date_of_birth else None,
            retired=data.retired,
            deceased=data.deceased,
            number=int(data.shirt_number),
            preferred_foot=data.preferred_foot,
            preferred_hand=data.preferred_hand,
            positions=data.positions_detailed or [data.position] or [data.primary_position] or None,
            salary=data.salary,
            market_value=data.proposed_market_value,
            contract_expiry=data.contract_until.date() if data.contract_until else None,
        )
