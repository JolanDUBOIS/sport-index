from __future__ import annotations

import logging
from abc import abstractmethod
from datetime import UTC, datetime
from functools import cached_property
from typing import TYPE_CHECKING, Any, overload

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

if TYPE_CHECKING:
    from sportindex.api_client import SofascoreProvider
    from sportindex.api_client.models import Round, _SeasonRoundsResponse

    from .competition import Competition, _StageCompetition, _TournamentCompetition
    from .core import Sport
    from .event import EventCollection
    from .leaderboard import Standings

logger = logging.getLogger(__name__)


class Season(IdentifiableEntity, EventAwareMixin):
    """One edition of a competition, e.g. 'Ligue 1 2024/25' or 'Formula 1 2025'.

    Instantiating `Season` returns one of two private variants depending on the payload:
    a match-based season (a league or tournament edition) or a stage-based season (a
    motorsport or cycling calendar). They differ in three places, noted per member below —
    rounds, standings, and what fixtures and results contain.

    A season's ID nests its competition's ID, so a season is only addressable together with
    its parent, e.g. "trnc:34:trns:61736". Constructing a match-based season directly
    therefore requires its competition to be supplied via the `competition` or
    `uniqueTournament` keyword; a stage-based season carries its own.

    Attributes:
        id (str): Globally unique SDK ID, of the form "<competition_id>:trns:<id>" for
            match-based seasons and "<competition_id>:stgs:<id>" for stage-based ones.
        name (str): Display name, e.g. "Ligue 1 24/25".
        year (str): The season's year label, e.g. "24/25" or "2025".
        start (datetime | None): When the season begins, if the provider states it.
        sport (Sport): The sport this season belongs to, taken from its competition.
        competition (Competition): The competition this season is an edition of.
        current_round (Round | None): The round currently being played. Always None for
            stage-based seasons, which have no rounds.
        rounds (list[Round] | None): Every round in the season. Always empty for stage-based
            seasons.
        standings (list[Standings]): The season's ranking tables. For a match-based season:
            up to three league tables — total, home and away — whichever the provider
            publishes. For a stage-based season: exactly two tables, individuals and teams,
            each empty if unavailable. Only current seasons generally have standings.
        source (_SeasonData | _StageData): The parsed payload backing this entity.
            (inherited from BaseEntity)

    Methods:
        get_fixtures(silent: bool = False) -> EventCollection: The season's upcoming events —
            `MatchEvent`s for a match-based season, `StageEvent`s for a stage-based one.
        get_results(silent: bool = False) -> EventCollection: The season's past events, same
            types as `get_fixtures`.
        get_events() -> EventCollection: Fixtures and results combined, sorted by start time.
            (inherited from EventAwareMixin)
        from_id(entity_id: str, provider: SofascoreProvider) -> Season: The season with this
            compound SDK ID. (classmethod, inherited from IdentifiableEntity)

    Raises:
        TypeError: If constructed with data that is neither `_SeasonData` nor `_StageData`.
        ValueError: If stage-based season data carries a tier other than SEASON.
        InsufficientDataError: If a match-based season is constructed without a `competition`
            or `uniqueTournament` keyword, or if a stage-based season's payload has no
            unique stage to derive its competition from.
        EntityNotFoundError: If `from_id` names a season the provider does not have.
        DomainError: If the provider fails with a network or transport error.
    """
    _data: _SeasonData | _StageData
    _REPR_FIELDS = ("id", "name", "year", "start", "sport")

    @overload
    def __new__(cls, data: _SeasonData, provider: SofascoreProvider, **kwargs) -> _TournamentSeason: ...

    @overload
    def __new__(cls, data: _StageData, provider: SofascoreProvider, **kwargs) -> _StageSeason: ...

    def __new__(cls, data: _SeasonData | _StageData, provider: SofascoreProvider, **kwargs):
        if cls is Season:
            if isinstance(data, _SeasonData):
                return object().__new__(_TournamentSeason)
            if isinstance(data, _StageData):
                return object().__new__(_StageSeason)
            raise TypeError(f"Season data must be either _SeasonData or _StageData, got {type(data)}")
        return super().__new__(cls)

    @property
    def id(self) -> str:
        """The unique ID of the season."""
        return self.encode_id(self._data.id, self.competition.id)

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
    def sport(self) -> Sport:
        """The sport this season belongs to."""
        return self.competition.sport

    @property
    @abstractmethod
    def competition(self) -> Competition:
        """The competition this season belongs to."""
        raise NotImplementedError("Subclasses of Season must implement the competition property")

    @property
    @abstractmethod
    def current_round(self) -> Round | None:
        """The current round of the season, if match-based season and available."""
        raise NotImplementedError("Subclasses of Season must implement the current_round property")

    @property
    @abstractmethod
    def rounds(self) -> list[Round] | None:
        """The list of rounds in the season, if match-based season."""
        raise NotImplementedError("Subclasses of Season must implement the rounds property")

    @property
    @abstractmethod
    def standings(self) -> list[Standings]:
        """Fetch all standings for this season (only available for current seasons)."""
        raise NotImplementedError("Subclasses of Season must implement the standings property")


class _TournamentSeason(Season):
    """Private `Season` variant for match-based competition editions; see `Season`."""
    _data: _SeasonData
    _PREFIX = "trns"

    def __init__(self, data: _SeasonData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)
        if not isinstance(data, _SeasonData):
            raise TypeError(f"Tournament season data must be of type _SeasonData, got {type(data)}")
        if not ("competition" in kwargs or "uniqueTournament" in kwargs):
            raise InsufficientDataError("Season data of type _SeasonData requires 'competition' or 'uniqueTournament' to be passed in via kwargs")

    @cached_property
    def competition(self) -> _TournamentCompetition:
        """The tournament competition this season belongs to."""
        from .competition import Competition
        if "competition" in self._kwargs:
            return self._kwargs["competition"]
        if "uniqueTournament" in self._kwargs:
            return Competition(self._kwargs["uniqueTournament"], self._provider)
        raise InsufficientDataError("Season data requires 'competition' or 'uniqueTournament' to be passed in via kwargs")

    @property
    def current_round(self) -> Round | None:
        """The current round of the season, if available."""
        return self._season_rounds.current_round

    @property
    def rounds(self) -> list[Round]:
        """The list of rounds in the season."""
        return self._season_rounds.rounds

    @cached_property
    def _season_rounds(self) -> _SeasonRoundsResponse:
        return self._provider.get_unique_tournament_rounds(self.competition._data.id, self._data.id)

    @property
    def standings(self) -> list[Standings]:
        """The league tables for this season — total, home and away, whichever the provider publishes."""
        from .leaderboard import Standings
        try:
            standings = self._provider.get_unique_tournament_standings(self.competition._data.id, self._data.id, view="total")
        except ProviderNotFoundError as e:
            logger.debug(f"Failed to fetch total standings for season {self.id}: {e}")
            standings = []
        try:
            standings.extend(self._provider.get_unique_tournament_standings(self.competition._data.id, self._data.id, view="home"))
        except ProviderNotFoundError as e:
            logger.debug(f"Failed to fetch home standings for season {self.id}: {e}")
        try:
            standings.extend(self._provider.get_unique_tournament_standings(self.competition._data.id, self._data.id, view="away"))
        except ProviderNotFoundError as e:
            logger.debug(f"Failed to fetch away standings for season {self.id}: {e}")
        return [Standings(s, self._provider) for s in standings]

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Fetch all fixtures for this season."""
        return self._fetch_paginated_events(
            self._provider.get_unique_tournament_fixtures,
            self.competition._data.id,
            self._data.id
        )

    def get_results(self, silent: bool = False) -> EventCollection:
        """Fetch all results for this season."""
        return self._fetch_paginated_events(
            self._provider.get_unique_tournament_results,
            self.competition._data.id,
            self._data.id
        )

    @classmethod
    def _process_parent_id(cls, parent_id: str, provider: SofascoreProvider) -> dict[str, Any]:
        from .competition import Competition
        return {"competition": Competition.from_id(parent_id, provider)}

    @staticmethod
    def _fetch_entity(raw_id: int, provider: SofascoreProvider, **kwargs) -> _SeasonData:
        """Fetch the season data from the provider by its raw ID."""
        try:
            ut_seasons = provider.get_unique_tournament_seasons(kwargs["competition"]._data.id)
            return next((s for s in ut_seasons if s.id == raw_id), None)
        except ProviderNotFoundError as e:
            logger.debug(f"Season with id {raw_id} not found: {e}")
            raise EntityNotFoundError(f"Season with id {raw_id} not found") from e
        except FetchError as e:
            logger.error(f"Network error while fetching season with id {raw_id}: {e}")
            raise DomainError(f"Network error while fetching season with id {raw_id}") from e


class _StageSeason(Season):
    """Private `Season` variant for stage-based competition editions; see `Season`."""
    _data: _StageData
    _PREFIX = "stgs"

    def __init__(self, data: _StageData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)
        if not isinstance(data, _StageData):
            raise TypeError(f"Stage season data must be of type _StageData, got {type(data)}")
        if data.tier and data.tier != StageTier.SEASON:
            raise ValueError(f"Stage-based season data must have tier SEASON, got {data.tier}")

    @cached_property
    def competition(self) -> _StageCompetition:
        """The stage competition this season belongs to."""
        from .competition import Competition
        if self._data.unique_stage:
            return Competition(self._data.unique_stage, self._provider)
        raise InsufficientDataError("Stage-based season data requires 'unique_stage' to be present in the data")

    @property
    def current_round(self) -> None:
        """Stage-based seasons do not have rounds, so this always returns None."""
        return None

    @property
    def rounds(self) -> list[Round]:
        """Stage-based seasons do not have rounds, so this always returns an empty list."""
        return []

    @property
    def standings(self) -> list[Standings]:
        """The two championship tables for this season — individuals and teams; either may be empty."""
        from sportindex.api_client.models import _RacingStandingsData

        from .leaderboard import Standings
        try:
            competitors_standings = self._provider.get_stage_standings_competitors(self._data.id)
        except ProviderNotFoundError as e:
            logger.debug(f"Failed to fetch competitors standings for stage {self.id}: {e}")
            competitors_standings = _RacingStandingsData()
        try:
            teams_standings = self._provider.get_stage_standings_teams(self._data.id)
        except ProviderNotFoundError as e:
            logger.debug(f"Failed to fetch teams standings for stage {self.id}: {e}")
            teams_standings = _RacingStandingsData()
        return [
            Standings(competitors_standings, self._provider, name=f"Individuals {self.name}", kind="individuals"),
            Standings(teams_standings, self._provider, name=f"Teams {self.name}", kind="teams")
        ]

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Fetch all fixtures for this season."""
        from .event import Event, EventCollection
        substages = self._provider.get_stage_substages(self._data.id)
        future_substages = [s for s in substages if s.start >= datetime.now(tz=UTC)]
        return EventCollection([Event(s, self._provider) for s in future_substages])

    def get_results(self, silent: bool = False) -> EventCollection:
        """Fetch all results for this season."""
        from .event import Event, EventCollection
        substages = self._provider.get_stage_substages(self._data.id)
        past_substages = [s for s in substages if s.start < datetime.now(tz=UTC)]
        return EventCollection([Event(s, self._provider) for s in past_substages])

    @staticmethod
    def _fetch_entity(raw_id: int, provider: SofascoreProvider, **kwargs) -> _StageData:
        """Fetch the stage season data from the provider by its raw ID."""
        try:
            return provider.get_stage(raw_id)
        except ProviderNotFoundError as e:
            logger.debug(f"Season with id {raw_id} not found: {e}")
            raise EntityNotFoundError(f"Season with id {raw_id} not found") from e
        except FetchError as e:
            logger.error(f"Network error while fetching season with id {raw_id}: {e}")
            raise DomainError(f"Network error while fetching season with id {raw_id}") from e
