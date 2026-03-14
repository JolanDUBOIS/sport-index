from __future__ import annotations

from functools import cached_property
from dataclasses import replace
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from . import logger
from .base import BaseEntity, EventAwareMixin, EntityCollection
from .core import Category, Sport
from sportindex.core.provider.parsed import (
    ParsedUniqueTournament, ParsedUniqueStage,
    ParsedSeason, ParsedStage
)

if TYPE_CHECKING:
    from .event import EventCollection
    from .leaderboard import Standings
    from sportindex.core.provider.parsed import ParsedSofascoreProvider


class Competition(BaseEntity[ParsedUniqueTournament | ParsedUniqueStage]):
    """A competition, e.g. 'Ligue 1', 'Rolland Garros', etc."""
    REPR_FIELDS = ("id", "name", "slug", "sport", "category")

    def __init__(self, data: ParsedUniqueTournament | ParsedUniqueStage, provider: ParsedSofascoreProvider | None = None, **kwargs) -> None:
        super().__init__(data, provider)

        if not isinstance(data, (ParsedUniqueTournament, ParsedUniqueStage)):
            raise ValueError("Competition data must be either ParsedUniqueTournament or ParsedUniqueStage")

        self._full_loaded = False

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
                for s in self._provider.get_unique_tournament_seasons(self.id)
            ])
        elif isinstance(self._data, ParsedUniqueStage):
            return EntityCollection([
                Season(s, self._provider, competition=self)
                for s in self._provider.get_unique_stage_seasons(self.id)
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
                self._data = replace(self._data, **vars(self._provider.get_unique_tournament(self.id)))
            elif isinstance(self._data, ParsedUniqueStage):
                logger.debug(f"No endpoint available to fully load unique stage yet, skipping full load...")
            assert isinstance(self._data, (ParsedUniqueTournament, ParsedUniqueStage))
            self._full_loaded = True
            self._clear_cache()
        except Exception as e:
            logger.debug(f"Failed to fully load competition with id {self.id}: {e}")

    def _clear_cache(self) -> None:
        """Clear cached properties."""
        self.__dict__.pop("category", None)
        self.__dict__.pop("seasons", None)


class Season(BaseEntity[ParsedSeason | ParsedStage], EventAwareMixin):
    """A season of a competition, e.g. '2023/24', '2024', etc."""
    REPR_FIELDS = ("id", "name", "year", "start", "sport")

    def __init__(self, data: ParsedSeason | ParsedStage, provider: ParsedSofascoreProvider | None = None, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, (ParsedSeason, ParsedStage)):
            raise ValueError("Season data must be either ParsedSeason or ParsedStage")

        if isinstance(data, ParsedStage) and data.type_.name != "Season":
            logger.warning(
                f"ParsedStage with id {data.id} has type '{data.type_.name}' "
                "instead of 'Season', but is being used to create a Season entity. "
                "This could lead to incorrect data being assigned to the Season entity. "
                "Please check the data and consider using a different entity type if appropriate."
            )

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
            from sportindex.core.provider.parsed import ParsedSeason, ParsedStage
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
    def standings(self) -> list[Standings]:
        """Fetch all standings for this season (only available for current seasons)."""
        from .leaderboard import Standings
        if isinstance(self._data, ParsedSeason):
            standings = self._provider.get_unique_tournament_standings(self.competition.id, self.id, view="total")
            try:
                standings.extend(self._provider.get_unique_tournament_standings(self.competition.id, self.id, view="home"))
            except Exception as e:
                logger.debug(f"Failed to fetch home standings for season {self.id}: {e}")
            try:
                standings.extend(self._provider.get_unique_tournament_standings(self.competition.id, self.id, view="away"))
            except Exception as e:
                logger.debug(f"Failed to fetch away standings for season {self.id}: {e}")
            return [Standings(s, self._provider) for s in standings]
        elif isinstance(self._data, ParsedStage):
            competitors_standings = self._provider.get_stage_standings_competitors(self.id)
            teams_standings = self._provider.get_stage_standings_teams(self.id)
            return [
                Standings(competitors_standings, self._provider, name=f"Competitors {self.name}", kind="competitors"),
                Standings(teams_standings, self._provider, name=f"Teams {self.name}", kind="teams")
            ]

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Fetch all fixtures for this season."""
        if isinstance(self._data, ParsedSeason):
            return self._fetch_paginated_events(
                self._provider.get_unique_tournament_fixtures, 
                self.competition.id, 
                self.id
            )
        elif isinstance(self._data, ParsedStage):
            from .event import Event, EventCollection
            substages = self._provider.get_stage_substages(self.id)
            future_substages = [s for s in substages if s.start >= datetime.now()]
            return EventCollection([Event(s, self._provider) for s in future_substages])

    def get_results(self, silent: bool = False) -> EventCollection:
        """Fetch all results for this season."""
        if isinstance(self._data, ParsedSeason):
            return self._fetch_paginated_events(
                self._provider.get_unique_tournament_results, 
                self.competition.id, 
                self.id
            )
        elif isinstance(self._data, ParsedStage):
            from .event import Event, EventCollection
            substages = self._provider.get_stage_substages(self.id)
            past_substages = [s for s in substages if s.end < datetime.now()]
            return EventCollection([Event(s, self._provider) for s in past_substages])

    def _clear_cache(self) -> None:
        """Clear cached properties."""
        self.__dict__.pop("competition", None)
