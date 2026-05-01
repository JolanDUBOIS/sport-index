from __future__ import annotations

import logging
from datetime import UTC, datetime
from functools import cached_property
from typing import TYPE_CHECKING, Literal, Self, overload

from typing_extensions import TypeVar

from sportindex.api_client.models import StageTier, _SeasonData, _StageData
from sportindex.exceptions import (
    DomainError,
    EntityNotFoundError,
    FetchError,
    InsufficientDataError,
    ProviderNotFoundError,
)

from .base import IdentifiableEntity
from .event import EventAwareMixin
from .types import SportContestNature
from .utils import merge_pydantic_models

if TYPE_CHECKING:
    from sportindex.api_client import SofascoreProvider
    from sportindex.api_client.models import BaseSchema, Round, _SeasonRoundsResponse

    from .competition import Competition
    from .core import Sport
    from .event import Event, EventCollection, MatchEvent, StageEvent
    from .leaderboard import Standings

logger = logging.getLogger(__name__)


E = TypeVar("E", bound="Event", default="Event")

class Season(IdentifiableEntity, EventAwareMixin[E]):
    """A season of a competition, e.g., '2023/24', '2024'.

    Provides access to parent competition, sport, standings, fixtures, and results.

    Attributes:
        id (int): Unique ID, encoded from source ID and type.
        name (str): Season name.
        year (str): Season year.
        start (Optional[datetime]): Start date of the season.
        sport (Sport): Parent sport.
        event_format (EventFormat): The event format for this season, either "match" or "stage".
        competition (Competition): Parent competition (lazy-loaded).
        current_round (Optional[Round]): Current round of the season, if available.
        rounds (Optional[list[Round]]): List of rounds in the season, if available.
        standings (list[Standings]): Standings for this season.

    Raises:
        TypeError: If data is not SeasonData or StageData, or if stage data has invalid tier.
        InsufficientDataError: If season data lacks required competition info.
        ValueError: If stage-based season data has a tier other than SEASON.
    """
    _data: _SeasonData | _StageData
    _REPR_FIELDS = ("id", "name", "year", "start", "sport")
    _N_TYPES: int = 2
    _TYPE_MAP: dict[type[BaseSchema], int] = {_SeasonData: 1, _StageData: 2}

    @overload
    def __new__(cls, data: _SeasonData, provider: SofascoreProvider, **kwargs) -> Season[MatchEvent]: ...

    @overload
    def __new__(cls, data: _StageData, provider: SofascoreProvider, **kwargs) -> Season[StageEvent]: ...

    def __new__(cls, data: _SeasonData | _StageData, provider: SofascoreProvider, **kwargs):
        return super().__new__(cls)

    def __init__(self, data: _SeasonData | _StageData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, (_SeasonData, _StageData)):
            raise TypeError(f"Season data must be either _SeasonData or _StageData, got {type(data)}")
        if isinstance(data, _SeasonData) and not ("competition" in kwargs or "uniqueTournament" in kwargs):
            raise InsufficientDataError("Season data of type _SeasonData requires 'competition' or 'uniqueTournament' to be passed in via kwargs")
        if isinstance(data, _StageData) and data.tier and data.tier != StageTier.SEASON:
            raise ValueError(f"Stage-based season data must have tier SEASON, got {data.tier}")

        self._full_loaded = False

    @property
    def id(self) -> int:
        """The unique ID of the season."""
        type_idx = self._TYPE_MAP[type(self._data)]
        return self.encode_id(self._data.id, type_idx, self.competition.id)

    @classmethod
    def encode_id(cls, raw_season_id: int, type_idx: int, competition_id: int) -> int:
        """
        Packs 3 variables into a single 52-bit integer.
        Format: [4 bits Type] [24 bits Competition ID] [24 bits Season ID]
        """
        if competition_id > 0xFFFFFF or raw_season_id > 0xFFFFFF:
            raise ValueError("Competition ID or Season ID exceeds 24-bit maximum (16.7M)")

        return (type_idx << 48) | (competition_id << 24) | raw_season_id

    @classmethod
    def decode_id(cls, encoded_id: int) -> tuple[int, int, int]:
        """
        Unpacks the 52-bit integer back into its parts.
        Returns: (raw_season_id, type_idx, competition_id)
        """
        raw_season_id = encoded_id & 0xFFFFFF
        competition_id = (encoded_id >> 24) & 0xFFFFFF
        type_idx = encoded_id >> 48

        return raw_season_id, type_idx, competition_id

    @property
    def name(self) -> str:
        """The name of the season."""
        return self._data.name

    @property
    def year(self) -> str:
        """The year of the season."""
        return self._data.year

    @property
    def start(self) -> datetime | None:
        """The start date of the season, if available."""
        return self._data.start

    @property
    def sport(self) -> Sport[E]:
        """The sport this season belongs to."""
        return self.competition.sport

    @property
    def sport_nature(self) -> SportContestNature:
        """The nature of the sport for this season."""
        if isinstance(self._data, _SeasonData):
            return SportContestNature.OPPOSITION
        if isinstance(self._data, _StageData):
            return SportContestNature.COMPARISON
        raise TypeError(f"Unsupported season data type {type(self._data)}.")

    @cached_property
    def competition(self) -> Competition:
        """The competition this season belongs to."""
        from .competition import Competition
        if "competition" in self._kwargs and isinstance(self._kwargs["competition"], Competition):
            return self._kwargs["competition"]
        if isinstance(self._data, _SeasonData):
            # _SeasonData doesn't contain any competition info, so it must be passed in via kwargs (either with competition key or uniqueTournament key)
            if "uniqueTournament" not in self._kwargs:
                raise InsufficientDataError("Season data requires 'competition' or 'uniqueTournament' to be passed in via kwargs")
            return Competition(self._kwargs["uniqueTournament"], self._provider)
        if isinstance(self._data, _StageData):
            if self._data.unique_stage:
                return Competition(self._data.unique_stage, self._provider)
            raise InsufficientDataError("Stage-based season data requires 'unique_stage' to be present in the data")
        raise TypeError(
            f"Unable to determine competition for season data type '{type(self._data).__name__}'. "
            "This data type is currently unsupported for competition mapping."
        )

    @property
    def current_round(self) -> Round | None:
        """The current round of the season, if match-based season and available."""
        return self._season_rounds.current_round if self._season_rounds else None

    @property
    def rounds(self) -> list[Round] | None:
        """The list of rounds in the season, if match-based season and available."""
        return self._season_rounds.rounds if self._season_rounds else None

    @cached_property
    def _season_rounds(self) -> _SeasonRoundsResponse | None:
        if isinstance(self._data, _SeasonData):
            return self._provider.get_unique_tournament_rounds(self.competition._data.id, self._data.id)
        if isinstance(self._data, _StageData):
            logger.debug("No rounds for stages, skipping fetch...")
            return None
        raise TypeError(f"Cannot fetch rounds for unknown data type: {type(self._data).__name__}")

    @property
    def standings(self) -> list[Standings]:
        """Fetch all standings for this season (only available for current seasons)."""
        from .leaderboard import Standings
        if isinstance(self._data, _SeasonData):
            standings = self._provider.get_unique_tournament_standings(self.competition._data.id, self._data.id, view="total")
            try:
                standings.extend(self._provider.get_unique_tournament_standings(self.competition._data.id, self._data.id, view="home"))
            except ProviderNotFoundError as e:
                logger.debug(f"Failed to fetch home standings for season {self.id}: {e}")
            try:
                standings.extend(self._provider.get_unique_tournament_standings(self.competition._data.id, self._data.id, view="away"))
            except ProviderNotFoundError as e:
                logger.debug(f"Failed to fetch away standings for season {self.id}: {e}")
            return [Standings(s, self._provider) for s in standings]
        if isinstance(self._data, _StageData):
            try:
                competitors_standings = self._provider.get_stage_standings_competitors(self._data.id)
            except ProviderNotFoundError as e:
                logger.debug(f"Failed to fetch competitors standings for stage {self.id}: {e}")
                competitors_standings = []
            try:
                teams_standings = self._provider.get_stage_standings_teams(self._data.id)
            except ProviderNotFoundError as e:
                logger.debug(f"Failed to fetch teams standings for stage {self.id}: {e}")
                teams_standings = []
            return [
                Standings(competitors_standings, self._provider, name=f"Individuals {self.name}", kind="individuals"),
                Standings(teams_standings, self._provider, name=f"Teams {self.name}", kind="teams")
            ]
        raise TypeError(f"Cannot fetch standings for unknown data type: {type(self._data).__name__}")

    def get_fixtures(self, silent: bool = False) -> EventCollection[E]:
        """Fetch all fixtures for this season."""
        if isinstance(self._data, _SeasonData):
            return self._fetch_paginated_events(
                self._provider.get_unique_tournament_fixtures,
                self.competition._data.id,
                self._data.id
            )
        if isinstance(self._data, _StageData):
            from .event import Event, EventCollection
            substages = self._provider.get_stage_substages(self._data.id)
            future_substages = [s for s in substages if s.start >= datetime.now(tz=UTC)]
            return EventCollection([Event(s, self._provider) for s in future_substages])
        raise TypeError(f"Cannot fetch fixtures for unknown data type: {type(self._data).__name__}")

    def get_results(self, silent: bool = False) -> EventCollection[E]:
        """Fetch all results for this season."""
        if isinstance(self._data, _SeasonData):
            return self._fetch_paginated_events(
                self._provider.get_unique_tournament_results,
                self.competition._data.id,
                self._data.id
            )
        if isinstance(self._data, _StageData):
            from .event import Event, EventCollection
            substages = self._provider.get_stage_substages(self._data.id)
            past_substages = [s for s in substages if s.end < datetime.now(tz=UTC)]
            return EventCollection([Event(s, self._provider) for s in past_substages])
        raise TypeError(f"Cannot fetch results for unknown data type: {type(self._data).__name__}")

    def _full_load(self) -> None:
        """
        Lazy-loads the complete season from the provider.
        Called automatically when accessing properties that require full details
        missing from the initial lightweight API response.
        """
        if self._full_loaded:
            return

        self._data = merge_pydantic_models(self._data, self._fetch_entity(self.id, self._provider, strict=False))

        self._full_loaded = True
        self._clear_cache()

    @classmethod
    def from_id(cls, season_id: int, provider: SofascoreProvider) -> Self:
        """Factory method to create a Season instance from an encoded ID."""
        if not isinstance(season_id, int):
            raise TypeError(f"Season ID must be an integer, got {type(season_id)}")

        try:
            _, type_idx, competition_id = cls.decode_id(season_id)
            entity_data = cls._fetch_entity(season_id, provider)

            kwargs = {}
            if type_idx == 1:
                from .competition import Competition
                kwargs["competition"] = Competition.from_id(competition_id, provider)

            instance = cls(entity_data, provider, **kwargs)
            if not issubclass(type(instance), cls):
                raise TypeError(
                    f"ID {season_id} belongs to a {type(instance).__name__}, but was initialized as a {cls.__name__}. "
                    f"This likely indicates a mismatch between the encoded type index and the expected season data types."
                )
            return instance
        except EntityNotFoundError as e:
            raise EntityNotFoundError(f"Season with ID {season_id} not found") from e
        except FetchError as e:
            raise DomainError(f"Network error while fetching season with ID {season_id}") from e

    @overload
    @classmethod
    def _fetch_entity(cls, competition_id: int, provider: SofascoreProvider, strict: Literal[True] = True) -> _SeasonData | _StageData: ...

    @overload
    @classmethod
    def _fetch_entity(cls, competition_id: int, provider: SofascoreProvider, strict: Literal[False]) -> _SeasonData | _StageData | None: ...

    @classmethod
    def _fetch_entity(cls, season_id: int, provider: SofascoreProvider, strict: bool = True) -> _SeasonData | _StageData | None:
        """Fetch the complete season data from the provider by its ID."""
        raw_id, type_idx, competition_id = cls.decode_id(season_id)

        try:
            if type_idx == 1:
                from .competition import Competition
                unique_tournament_id, _ = Competition.decode_id(competition_id)
                return cls._fetch_season_data(raw_id, unique_tournament_id, provider)
            if type_idx == 2:
                return cls._fetch_stage_data(raw_id, provider)
            raise TypeError(f"Invalid season ID {season_id}: unknown type index {type_idx}")

        except ProviderNotFoundError:
            logger.debug(f"Season with ID {season_id} not found during fetch")
            if strict:
                raise EntityNotFoundError(f"Season with ID {season_id} not found during fetch") from None

        except FetchError as e:
            logger.debug(f"Network error while fetching season with ID {season_id}: {e}")
            if strict:
                raise DomainError(f"Network error while fetching season with ID {season_id}") from e

        return None

    @staticmethod
    def _fetch_season_data(season_data_id: int, unique_tournament_id: int, provider: SofascoreProvider) -> _SeasonData:
        """Fetch _SeasonData by raw ID."""
        ut_seasons = provider.get_unique_tournament_seasons(unique_tournament_id)
        return next((s for s in ut_seasons if s.id == season_data_id), None)

    @staticmethod
    def _fetch_stage_data(stage_data_id: int, provider: SofascoreProvider) -> _StageData:
        """Fetch _StageData by raw ID."""
        return provider.get_stage(stage_data_id)
