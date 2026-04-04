from __future__ import annotations

from functools import cached_property
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, TypeVar, overload

from . import logger
from .base import IdentifiableEntity, EntityCollection
from .event import Event, EventAwareMixin
from .types import EventFormat
from .utils import merge_pydantic_models
from sportindex.exceptions import InsufficientDataError, ProviderNotFoundError, FetchError
from sportindex.provider.models import _SeasonData, _StageData

if TYPE_CHECKING:
    from .competition import Competition
    from .core import Sport
    from .event import MatchEvent, StageEvent, EventCollection
    from .leaderboard import Standings
    from sportindex.provider import SofascoreProvider
    from sportindex.provider.models import BaseSchema, Round, _SeasonRoundsResponse


E = TypeVar("E", bound=Event)

class Season(IdentifiableEntity, EventAwareMixin[E]):
    """A season of a competition, e.g., '2023/24', '2024'.

    Provides access to parent competition, sport, standings, fixtures, and results.

    Attributes:
        id (int): Unique ID, encoded from source ID and type.
        name (str): Season name.
        year (str): Season year.
        start (Optional[datetime]): Start date of the season.
        sport (Sport): Parent sport.
        competition (Competition): Parent competition (lazy-loaded).
        current_round (Optional[Round]): Current round of the season, if available.
        rounds (Optional[list[Round]]): List of rounds in the season, if available.
        standings (EntityCollection[Standings]): Standings for this season.

    Raises:
        InsufficientDataError: If season data lacks required competition info.
    """
    _data: _SeasonData | _StageData
    _REPR_FIELDS = ("id", "name", "year", "start", "sport")
    _TYPE_MAP: dict[type[BaseSchema], int] = {_SeasonData: 1, _StageData: 2}
    _FORMAT_MAP: dict[type[BaseSchema], str] = {_SeasonData: "match", _StageData: "stage"}

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

        self._full_loaded = False

    @property
    def id(self) -> int:
        """The unique ID of the season."""
        type_idx = self._TYPE_MAP[type(self._data)]
        return self.encode_id(self._data.id, type_idx)

    @property
    def name(self) -> str:
        """The name of the season."""
        return self._data.name

    @property
    def year(self) -> str:
        """The year of the season."""
        return self._data.year

    @property
    def start(self) -> Optional[datetime]:
        """The start date of the season, if available."""
        return self._data.start

    @property
    def sport(self) -> Sport:
        """The sport this season belongs to."""
        return self.competition.sport

    @property
    def format(self) -> EventFormat:
        """The event format for this season."""
        try:
            return self._FORMAT_MAP.get(type(self._data))
        except KeyError:
            raise TypeError(f"Unsupported season data type {type(self._data)}.")

    @cached_property
    def competition(self) -> Competition:
        """The competition this season belongs to."""
        from .competition import Competition
        if "competition" in self._kwargs and isinstance(self._kwargs["competition"], Competition):
            return self._kwargs["competition"]
        else:
            if isinstance(self._data, _SeasonData):
                # _SeasonData doesn't contain any competition info, so it must be passed in via kwargs (either with competition key or uniqueTournament key)
                if "uniqueTournament" not in self._kwargs:
                    raise InsufficientDataError("Season data requires 'competition' or 'uniqueTournament' to be passed in via kwargs")
                return Competition(self._kwargs["uniqueTournament"], self._provider)
            elif isinstance(self._data, _StageData):
                return Competition(self._data.unique_stage, self._provider)

    @property
    def current_round(self) -> Optional[Round]:
        """The current round of the season, if match-based season and available."""
        return self._season_rounds.current_round if self._season_rounds else None

    @property
    def rounds(self) -> Optional[list[Round]]:
        """The list of rounds in the season, if match-based season and available."""
        return self._season_rounds.rounds if self._season_rounds else None

    @cached_property
    def _season_rounds(self) -> Optional[_SeasonRoundsResponse]:
        if isinstance(self._data, _SeasonData):
            return self._provider.get_unique_tournament_rounds(self.competition._data.id, self._data.id)
        elif isinstance(self._data, _StageData):
            logger.debug(f"No rounds for stages, skipping fetch...")
            return None

    @property
    def standings(self) -> EntityCollection[Standings]:
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
            return EntityCollection([Standings(s, self._provider) for s in standings])
        elif isinstance(self._data, _StageData):
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
            return EntityCollection([
                Standings(competitors_standings, self._provider, name=f"Individuals {self.name}", kind="individuals"),
                Standings(teams_standings, self._provider, name=f"Teams {self.name}", kind="teams")
            ])

    def get_fixtures(self, silent: bool = False) -> EventCollection[E]:
        """Fetch all fixtures for this season."""
        if isinstance(self._data, _SeasonData):
            return self._fetch_paginated_events(
                self._provider.get_unique_tournament_fixtures, 
                self.competition._data.id, 
                self._data.id
            )
        elif isinstance(self._data, _StageData):
            from .event import Event, EventCollection
            substages = self._provider.get_stage_substages(self._data.id)
            future_substages = [s for s in substages if s.start >= datetime.now(tz=timezone.utc)]
            return EventCollection([Event(s, self._provider) for s in future_substages])

    def get_results(self, silent: bool = False) -> EventCollection[E]:
        """Fetch all results for this season."""
        if isinstance(self._data, _SeasonData):
            return self._fetch_paginated_events(
                self._provider.get_unique_tournament_results, 
                self.competition._data.id, 
                self._data.id
            )
        elif isinstance(self._data, _StageData):
            from .event import Event, EventCollection
            substages = self._provider.get_stage_substages(self._data.id)
            past_substages = [s for s in substages if s.end < datetime.now(tz=timezone.utc)]
            return EventCollection([Event(s, self._provider) for s in past_substages])

    def _full_load(self) -> None:
        """
        Lazy-loads the complete season from the provider.
        Called automatically when accessing properties that require full details
        missing from the initial lightweight API response.
        """
        if self._full_loaded:
            return
        try:
            if isinstance(self._data, _SeasonData):
                logger.info("No endpoint available to fully load unique tournament season yet, skipping full load...")
            elif isinstance(self._data, _StageData):
                self._data = merge_pydantic_models(self._data, self._provider.get_stage(self._data.id))
                if self._data.tier is not None and self._data.tier.name.lower() != "season":
                    logger.warning(
                        f"_StageData with id {self._data.id} has tier '{self._data.tier.name}' "
                        "instead of 'Season', but is being used to create a Season entity. "
                        "This could lead to incorrect data being assigned to the Season entity. "
                        "Please check the data and consider using a different entity tier if appropriate."
                    )
        except ProviderNotFoundError:
            logger.debug(f"Season with id {self._data.id} not found during full load")
        except FetchError as e:
            logger.debug(f"Network error while fully loading season with id {self._data.id}: {e}")
        self._full_loaded = True
        self._clear_cache()
