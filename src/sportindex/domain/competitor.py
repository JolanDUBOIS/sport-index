from __future__ import annotations

from functools import cached_property
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Optional, Literal

from . import logger
from .base import BaseEntity, EventAwareMixin, EntityCollection
from .utils import merge_dataclasses
from sportindex.provider import NotFoundError, FetchError
from sportindex.provider.parsed import ParsedTeam, ParsedPlayer
from sportindex.provider.raw import Amount as Amount

if TYPE_CHECKING:
    from .core import Category, Country, Sport, Gender
    from .event import EventCollection
    from .manager import Manager
    from .venue import Venue
    from sportindex.provider.parsed import (
        ParsedSofascoreProvider, ParsedPlayerTeamInfo
    )


class Competitor(BaseEntity[ParsedTeam | ParsedPlayer], EventAwareMixin):
    """A competitor, e.g. 'Paris Saint-Germain', 'Roger Federer', 'Lewis Hamilton', etc."""
    REPR_FIELDS = ("id", "name", "slug", "short_name", "full_name", "name_code", "national", "gender", "sport", "country", "category", "kind")
    _TYPE_MAP = {ParsedTeam: 1, ParsedPlayer: 2}

    def __init__(self, data: ParsedTeam | ParsedPlayer, provider: ParsedSofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, (ParsedTeam, ParsedPlayer)):
            raise ValueError("Competitor data must be either ParsedTeam or ParsedPlayer")

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
        if isinstance(self._data, ParsedTeam):
            return self._data.fullName
        elif isinstance(self._data, ParsedPlayer):
            return self._data.firstName + " " + self._data.lastName

    @property
    def name_code(self) -> Optional[str]:
        """The name code of the competitor, if applicable."""
        if isinstance(self._data, ParsedTeam):
            return self._data.nameCode
        else:
            return None

    @property
    def national(self) -> Optional[bool]:
        """Whether this competitor is a national team."""
        if isinstance(self._data, ParsedTeam):
            return self._data.national
        else:
            return None

    # --- Properties to be cached, as they require additional API calls or processing (even if they are quite light) ---

    @cached_property
    def gender(self) -> Optional[Gender]:
        """The gender of the competitor, if applicable."""
        from .core import Gender
        return Gender(self._data.gender)

    @cached_property
    def sport(self) -> Optional[Sport]:
        """The sport this competitor belongs to."""
        from .core import Sport
        if isinstance(self._data, ParsedTeam):
            return Sport(self._data.sport, self._provider) if self._data.sport else None
        elif isinstance(self._data, ParsedPlayer):
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
        if isinstance(self._data, ParsedTeam):
            return Category(self._data.category, self._provider) if self._data.category else None
        elif isinstance(self._data, ParsedPlayer):
            return Category(self._data.team.category, self._provider) if self._data.team and self._data.team.category else None

    @cached_property
    def kind(self) -> Literal["team", "player"]:
        """Whether this competitor is a team or a player."""
        if isinstance(self._data, ParsedPlayer):
            return "player"
        elif isinstance(self._data, ParsedTeam):
            if self._data.playerTeamInfo is not None:
                logger.debug(f"Team {self._data.name} has playerTeamInfo, treating it as a player")
                return "player"
            else:
                return "team"

    @cached_property
    def parent(self) -> Optional[Competitor]:
        """The parent competitor, if this is a player belonging to a team."""
        self._full_load()
        if isinstance(self._data, ParsedPlayer) and self._data.team is not None:
            return Competitor(self._data.team, self._provider)
        elif isinstance(self._data, ParsedTeam) and self._data.parentTeam is not None:
            return Competitor(self._data.parentTeam, self._provider)
        else:
            return None

    @cached_property
    def players(self) -> Optional[EntityCollection[Competitor]]:
        """The players belonging to this competitor, if this is a team."""
        if not isinstance(self._data, ParsedTeam):
            return None
        try:
            return EntityCollection([Competitor(player, self._provider) for player in self._provider.get_team_players(self._data.id).players])
        except NotFoundError:
            logger.debug(f"No players found for team with id {self.id}, returning empty collection")
            return EntityCollection([])

    @cached_property
    def drivers(self) -> Optional[EntityCollection[Competitor]]:
        """The drivers belonging to this competitor, if this is a motorsport team."""
        if not isinstance(self._data, ParsedTeam):
            return None
        try:
            return EntityCollection([Competitor(driver, self._provider) for driver in self._provider.get_team(self._data.id).drivers])
        except NotFoundError:
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
        if isinstance(self._data, ParsedPlayer):
            return PlayerInfo._from_parsed_player(self._data)
        elif isinstance(self._data, ParsedTeam) and self._data.playerTeamInfo is not None:
            return PlayerInfo._from_parsed_player_team_info(self._data.playerTeamInfo)
        else:
            return None

    # --- Properties to be recomputed each time, as they might change regularly ---

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Fetch all fixtures for this competitor."""
        if isinstance(self._data, ParsedPlayer):
            if not silent:
                logger.warning(f"No fixtures endpoint for non individual sports players like {self.name}, returning empty list")
            from .event import EventCollection
            return EventCollection([])
        elif isinstance(self._data, ParsedTeam):
            return self._fetch_paginated_events(self._provider.get_team_fixtures, self._data.id)
        from .event import EventCollection
        return EventCollection([])

    def get_results(self, silent: bool = False) -> EventCollection:
        """Fetch all results for this competitor."""
        if isinstance(self._data, ParsedPlayer):
            return self._fetch_paginated_events(self._provider.get_player_results, self._data.id)
        elif isinstance(self._data, ParsedTeam):
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
            if isinstance(self._data, ParsedPlayer):
                self._data = merge_dataclasses(self._data, self._provider.get_player(self._data.id))
            elif isinstance(self._data, ParsedTeam):
                self._data = merge_dataclasses(self._data, self._provider.get_team(self._data.id))
            assert isinstance(self._data, (ParsedPlayer, ParsedTeam))
            self._full_loaded = True
            self._clear_cache()
        except NotFoundError:
            logger.debug(f"Competitor with id {self._data.id} not found during full load.")
            self._full_loaded = True
        except FetchError as e:
            logger.debug(f"Network error while fully loading competitor with id {self._data.id}: {e}")

    def _clear_cache(self) -> None:
        """Clear cached properties."""
        self.__dict__.pop("gender", None)
        self.__dict__.pop("sport", None)
        self.__dict__.pop("country", None)
        self.__dict__.pop("category", None)
        self.__dict__.pop("kind", None)
        self.__dict__.pop("parent", None)
        self.__dict__.pop("players", None)
        self.__dict__.pop("drivers", None)
        self.__dict__.pop("manager", None)
        self.__dict__.pop("venue", None)
        self.__dict__.pop("player_info", None)

    @classmethod
    def from_id(cls, competitor_id: int, provider: ParsedSofascoreProvider) -> Competitor:
        """Fetch a competitor by its ID."""
        raw_id, type_idx = cls.decode_id(competitor_id)
        type_map_reverse = {v: k for k, v in cls._TYPE_MAP.items()}

        if type_idx not in type_map_reverse:
            raise ValueError(f"Invalid competitor ID {competitor_id}: unknown type index {type_idx}")

        data_cls = type_map_reverse[type_idx]
        if data_cls == ParsedTeam:
            parsed_data = provider.get_team(raw_id).team
        elif data_cls == ParsedPlayer:
            parsed_data = provider.get_player(raw_id)
        else:
            raise ValueError(f"Unsupported competitor type index {type_idx} in ID {competitor_id}")

        return cls(parsed_data, provider)

    @classmethod
    def search(cls, query: str, provider: ParsedSofascoreProvider) -> EntityCollection[Competitor]:
        """Search for competitors matching the given query (up to the first 20 matches)."""
        entities = []
        for page in range(51):
            try:
                all_matches = provider.search_all(query=query, page=page)
            except (NotFoundError, FetchError):
                logger.debug(f"Failed to fetch search results for query '{query}' on page {page}, stopping pagination")
                break
            if not all_matches:
                break
            for item in all_matches:
                if isinstance(item.entity, (ParsedTeam, ParsedPlayer)):
                    entities.append(Competitor(item.entity, provider))
            if len(all_matches) > 20:
                break
        return EntityCollection(entities[:20])


@dataclass(frozen=True)
class PlayerInfo:
    """Comprehensive details covering a player's physical attributes, career status, and financial data."""

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
    def _from_parsed_player_team_info(cls, data: ParsedPlayerTeamInfo) -> PlayerInfo:
        """Create a PlayerInfo instance from ParsedPlayerTeamInfo data."""
        return cls(
            weight=float(data.weight),
            height=int(data.height * 100),
            date_of_birth=data.birthDate.date() if data.birthDate else None,
            place_of_birth=data.birthplace,
            number=int(data.number),
            preferred_foot=data.plays, # Note: probably never populated, as there are not single sport using the foot preference field...
            preferred_hand=data.plays,
            total_prizes=data.prizeTotalRaw,
        )

    @classmethod
    def _from_parsed_player(cls, data: ParsedPlayer) -> PlayerInfo:
        """Create a PlayerInfo instance from ParsedPlayer data."""
        return cls(
            first_name=data.firstName,
            last_name=data.lastName,
            weight=float(data.weight),
            height=int(data.height),
            date_of_birth=data.dateOfBirth.date() if data.dateOfBirth else None,
            retired=data.retired,
            deceased=data.deceased,
            number=int(data.shirtNumber),
            preferred_foot=data.preferredFoot,
            preferred_hand=data.preferredHand,
            positions=data.positionsDetailed or [data.position] or [data.primaryPosition] or None,
            salary=data.salaryRaw,
            market_value=data.proposedMarketValueRaw,
            contract_expiry=data.contractUntil.date() if data.contractUntil else None,
        )
