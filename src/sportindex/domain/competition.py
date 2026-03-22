from __future__ import annotations

from functools import cached_property
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from . import logger
from .base import BaseEntity, EventAwareMixin, EntityCollection
from .core import Category, Sport
from sportindex.provider.parsed import (
    ParsedUniqueTournament, ParsedUniqueStage,
    ParsedSeason, ParsedStage
)
from .utils import merge_dataclasses
from sportindex.provider import NotFoundError, FetchError

if TYPE_CHECKING:
    from .event import EventCollection
    from .leaderboard import Standings
    from sportindex.provider.parsed import ParsedSofascoreProvider


class Competition(BaseEntity[ParsedUniqueTournament | ParsedUniqueStage]):
    """A competition, e.g. 'Ligue 1', 'Rolland Garros', etc."""
    REPR_FIELDS = ("id", "name", "slug", "sport", "category")
    _TYPE_MAP = {ParsedUniqueTournament: 1, ParsedUniqueStage: 2}

    def __init__(self, data: ParsedUniqueTournament | ParsedUniqueStage, provider: ParsedSofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider)

        if not isinstance(data, (ParsedUniqueTournament, ParsedUniqueStage)):
            raise ValueError("Competition data must be either ParsedUniqueTournament or ParsedUniqueStage")

        self._full_loaded = False

    @property
    def id(self) -> int:
        """The unique ID of the competition."""
        type_idx = self._TYPE_MAP[type(self._data)]
        return self.encode_id(self._data.id, type_idx)

    @property
    def name(self) -> str:
        """The name of the competition."""
        return self._data.name

    @property
    def slug(self) -> str:
        """The slug of the competition."""
        return self._data.slug

    @property
    def sport(self) -> Sport:
        """The sport this competition belongs to."""
        return self.category.sport

    @cached_property
    def category(self) -> Category:
        """The category this competition belongs to."""
        return Category(self._data.category, self._provider)

    @cached_property
    def seasons(self) -> EntityCollection[Season]:
        """Fetch all seasons for this competition."""
        if isinstance(self._data, ParsedUniqueTournament):
            return EntityCollection([
                Season(s, self._provider, competition=self)
                for s in self._provider.get_unique_tournament_seasons(self._data.id)
            ])
        elif isinstance(self._data, ParsedUniqueStage):
            return EntityCollection([
                Season(s, self._provider, competition=self)
                for s in self._provider.get_unique_stage_seasons(self._data.id)
            ])
        else:
            raise ValueError("Competition data must be either ParsedUniqueTournament or ParsedUniqueStage")

    def _full_load(self) -> None:
        """
        Lazy-loads the complete competition from the provider.
        Called automatically when accessing properties that require full details
        missing from the initial lightweight API response.
        """
        if self._full_loaded:
            return
        try:
            if isinstance(self._data, ParsedUniqueTournament):
                self._data = merge_dataclasses(self._data, self._provider.get_unique_tournament(self._data.id))
            elif isinstance(self._data, ParsedUniqueStage):
                logger.debug(f"No endpoint available to fully load unique stage yet, skipping full load...")
            assert isinstance(self._data, (ParsedUniqueTournament, ParsedUniqueStage))
            self._full_loaded = True
            self._clear_cache()
        except NotFoundError:
            logger.debug(f"Competition with id {self._data.id} not found during full load.")
            self._full_loaded = True
        except FetchError as e:
            logger.debug(f"Network error while fully loading competition with id {self._data.id}: {e}")

    def _clear_cache(self) -> None:
        """Clear cached properties."""
        self.__dict__.pop("category", None)
        self.__dict__.pop("seasons", None)

    @classmethod
    def from_id(cls, competition_id: int, provider: ParsedSofascoreProvider) -> Competition:
        """Fetch a competition by its ID."""
        raw_id, type_idx = cls.decode_id(competition_id)
        type_map_reverse = {v: k for k, v in cls._TYPE_MAP.items()}

        if type_idx not in type_map_reverse:
            raise ValueError(f"Invalid competition ID {competition_id}: unknown type index {type_idx}")

        data_cls = type_map_reverse[type_idx]
        if data_cls == ParsedUniqueTournament:
            parsed_data = provider.get_unique_tournament(raw_id)
        elif data_cls == ParsedUniqueStage:
            us_seasons = provider.get_unique_stage_seasons(raw_id)
            if us_seasons:
                parsed_data = us_seasons[0].uniqueStage
            else:
                raise ValueError(f"Could not find any seasons for unique stage with ID {raw_id}, cannot construct competition")
        else:
            raise ValueError(f"Unsupported data class {data_cls} for competition ID {competition_id}")

        return cls(parsed_data, provider)

    @classmethod
    def search(cls, query: str, provider: ParsedSofascoreProvider) -> EntityCollection[Competition]:
        """Search for competitions matching the given query (up to the first 20 matches)."""
        entities = []
        for page in range(51): # Sofascore has a maximum of 50 pages of search results
            all_matches = provider.search_all(query=query, page=page)
            if not all_matches:
                break
            for item in all_matches:
                if isinstance(item.entity, (ParsedUniqueTournament, ParsedUniqueStage)):
                    entities.append(Competition(item.entity, provider))
            if len(all_matches) > 20:
                break
        return EntityCollection(entities[:20])


class Season(BaseEntity[ParsedSeason | ParsedStage], EventAwareMixin):
    """A season of a competition, e.g. '2023/24', '2024', etc."""
    REPR_FIELDS = ("id", "name", "year", "start", "sport")
    _TYPE_MAP = {ParsedSeason: 1, ParsedStage: 2}

    def __init__(self, data: ParsedSeason | ParsedStage, provider: ParsedSofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, (ParsedSeason, ParsedStage)):
            raise ValueError("Season data must be either ParsedSeason or ParsedStage")

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

    @cached_property
    def competition(self) -> Competition:
        """The competition this season belongs to."""
        if "competition" in self._kwargs and isinstance(self._kwargs["competition"], Competition):
            return self._kwargs["competition"]
        else:
            from sportindex.provider.parsed import ParsedSeason, ParsedStage
            if isinstance(self._data, ParsedSeason):
                # ParsedSeason doesn't contain any competition info, so it must be passed in via kwargs (either with competition key or uniqueTournament key)
                if "uniqueTournament" not in self._kwargs:
                    raise ValueError("ParsedSeason requires 'competition' or 'uniqueTournament' to be passed in via kwargs")
                return Competition(self._kwargs["uniqueTournament"], self._provider)
            elif isinstance(self._data, ParsedStage):
                return Competition(self._data.uniqueStage, self._provider)
            else:
                raise ValueError("Season data must be either ParsedSeason or ParsedStage")

    @property
    def standings(self) -> EntityCollection[Standings]:
        """Fetch all standings for this season (only available for current seasons)."""
        from .leaderboard import Standings
        if isinstance(self._data, ParsedSeason):
            standings = self._provider.get_unique_tournament_standings(self.competition._data.id, self._data.id, view="total")
            try:
                standings.extend(self._provider.get_unique_tournament_standings(self.competition._data.id, self._data.id, view="home"))
            except NotFoundError as e:
                logger.debug(f"Failed to fetch home standings for season {self.id}: {e}")
            try:
                standings.extend(self._provider.get_unique_tournament_standings(self.competition._data.id, self._data.id, view="away"))
            except NotFoundError as e:
                logger.debug(f"Failed to fetch away standings for season {self.id}: {e}")
            return EntityCollection([Standings(s, self._provider) for s in standings])
        elif isinstance(self._data, ParsedStage):
            try:
                competitors_standings = self._provider.get_stage_standings_competitors(self._data.id)
            except NotFoundError as e:
                logger.debug(f"Failed to fetch competitors standings for stage {self.id}: {e}")
                competitors_standings = []
            try:
                teams_standings = self._provider.get_stage_standings_teams(self._data.id)
            except NotFoundError as e:
                logger.debug(f"Failed to fetch teams standings for stage {self.id}: {e}")
                teams_standings = []
            return EntityCollection([
                Standings(competitors_standings, self._provider, name=f"Individuals {self.name}", kind="individuals"),
                Standings(teams_standings, self._provider, name=f"Teams {self.name}", kind="teams")
            ])

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Fetch all fixtures for this season."""
        if isinstance(self._data, ParsedSeason):
            return self._fetch_paginated_events(
                self._provider.get_unique_tournament_fixtures, 
                self.competition._data.id, 
                self._data.id
            )
        elif isinstance(self._data, ParsedStage):
            from .event import Event, EventCollection
            substages = self._provider.get_stage_substages(self._data.id)
            future_substages = [s for s in substages if s.start >= datetime.now()]
            return EventCollection([Event(s, self._provider) for s in future_substages])

    def get_results(self, silent: bool = False) -> EventCollection:
        """Fetch all results for this season."""
        if isinstance(self._data, ParsedSeason):
            return self._fetch_paginated_events(
                self._provider.get_unique_tournament_results, 
                self.competition._data.id, 
                self._data.id
            )
        elif isinstance(self._data, ParsedStage):
            from .event import Event, EventCollection
            substages = self._provider.get_stage_substages(self._data.id)
            past_substages = [s for s in substages if s.end < datetime.now()]
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
            if isinstance(self._data, ParsedSeason):
                logger.info("No endpoint available to fully load unique tournament season yet, skipping full load...")
            elif isinstance(self._data, ParsedStage):
                self._data = merge_dataclasses(self._data, self._provider.get_stage(self._data.id))
                if self._data.type_ is not None and self._data.type_.get("name") != "Season":
                    logger.warning(
                        f"ParsedStage with id {self._data.id} has type '{self._data.type_.get('name')}' "
                        "instead of 'Season', but is being used to create a Season entity. "
                        "This could lead to incorrect data being assigned to the Season entity. "
                        "Please check the data and consider using a different entity type if appropriate."
                    )
            assert isinstance(self._data, (ParsedSeason, ParsedStage))
            self._full_loaded = True
            self._clear_cache()
        except NotFoundError:
            logger.debug(f"Season with id {self._data.id} not found during full load.")
            self._full_loaded = True
        except FetchError as e:
            logger.debug(f"Network error while fully loading season with id {self._data.id}: {e}")

    def _clear_cache(self) -> None:
        """Clear cached properties."""
        self.__dict__.pop("competition", None)
