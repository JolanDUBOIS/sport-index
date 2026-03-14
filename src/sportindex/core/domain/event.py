from __future__ import annotations

from functools import cached_property
from dataclasses import dataclass, replace
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Literal

from . import logger
from .base import BaseEntity
from .core import Sport
from .competition import Season
from sportindex.core.provider.parsed import ParsedEvent, ParsedStage

if TYPE_CHECKING:
    from .channel import EventChannels
    from .competition import Competition
    from .competitor import Competitor
    from .leaderboard import Standings
    from .venue import Venue
    from sportindex.core.provider.parsed import (
        ParsedSofascoreProvider,
        ParsedLineupsResponse, ParsedIncident, 
        ParsedEventStatisticsResponse, 
        ParsedMomentumGraphResponse, ParsedPeriod
    )
    from sportindex.core.provider.raw import Round


class Event(BaseEntity[ParsedEvent | ParsedStage]):
    """An event, e.g. a football match, a tennis match, a formula one race, etc."""
    REPR_FIELDS = ("id", "name", "slug", "start", "kind", "end", "round", "competitors")

    def __init__(self, data: ParsedEvent | ParsedStage, provider: ParsedSofascoreProvider | None = None, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, (ParsedEvent, ParsedStage)):
            raise ValueError("Event data must be either ParsedEvent or ParsedStage")

        self._full_loaded = False

    @property
    def name(self) -> str:
        """The name of the event."""
        return self._data.name if hasattr(self._data, "name") and self._data.name else self._data.slug.replace("-", " ").title()

    @property
    def slug(self) -> str:
        """The slug of the event (used in URLs)."""
        return self._data.slug

    @property
    def start(self) -> datetime:
        """The start time of the event."""
        return self._data.start

    @property
    def kind(self) -> Literal["match", "race"]:
        """The kind of the event (match or race)."""
        return "match" if isinstance(self._data, ParsedEvent) else "race"

    @property
    def end(self) -> Optional[datetime]:
        """The end time of the event, if available."""
        return self._data.end if hasattr(self._data, "end") else None

    @property
    def round(self) -> Optional[Round]:
        """The round of the event, if available."""
        return self._data.roundInfo if hasattr(self._data, "roundInfo") else None

    @property
    def sport(self) -> Sport:
        """The sport this event belongs to."""
        return self.season.sport

    @cached_property
    def season(self) -> Season:
        """The season this event belongs to."""
        from sportindex.core.provider.parsed import ParsedEvent, ParsedStage
        if isinstance(self._data, ParsedEvent):
            return Season(self._data.season, self._provider, uniqueTournament=self._data.tournament.uniqueTournament)
        elif isinstance(self._data, ParsedStage):
            parent_stage_id = self._data.stageParent.id
            parent_stage = self._provider.get_stage(parent_stage_id)
            return Season(parent_stage, self._provider)
        else:
            raise ValueError("Event data must be either ParsedEvent or ParsedStage to determine season")

    @property
    def competition(self) -> Competition:
        """The competition this event belongs to."""
        return self.season.competition

    @cached_property
    def venue(self) -> Venue | None:
        """The venue where this event takes place, if available."""
        from .venue import Venue
        if isinstance(self._data, ParsedEvent) and self._data.venue:
            return Venue(self._data.venue, self._provider)
        elif isinstance(self._data, ParsedStage):
            return Venue(self._data, self._provider)

    @property
    def channels(self) -> EventChannels:
        """Get the channels broadcasting this event, if match and available."""
        from .channel import EventChannels
        if isinstance(self._data, ParsedEvent):
            return EventChannels(self._provider.get_event_channels(self.id), self._provider)
        elif isinstance(self._data, ParsedStage):
            return EventChannels(self._provider.get_stage_channels(self.id), self._provider)


    # Match specific properties

    @cached_property
    def competitors(self) -> MatchCompetitors | None:
        """The competitors in this event, if match and available."""
        if isinstance(self._data, ParsedEvent):
            try:
                from .competitor import Competitor
                return MatchCompetitors(
                    home=Competitor(self._data.home.team, self._provider),
                    away=Competitor(self._data.away.team, self._provider)
                )
            except Exception:
                logger.exception(f"Failed to parse competitors for event {self.id}.")
                raise
        return None

    @property
    def score(self) -> MatchScore | None:
        """The score for this event, if match and available."""
        if isinstance(self._data, ParsedEvent):
            try:
                return MatchScore(
                    home=self._data.home.score,
                    away=self._data.away.score
                )
            except Exception:
                logger.exception(f"Failed to parse score for event {self.id}.")
                return None
        return None

    @property
    def periods(self) -> list[ParsedPeriod] | None:
        """The periods for this event, if match and available."""
        if isinstance(self._data, ParsedEvent):
            try:
                return self._data.parsedPeriods.periods
            except Exception:
                logger.exception(f"Failed to parse periods for event {self.id}.")
                return None
        return None

    @cached_property
    def lineups(self) -> ParsedLineupsResponse | None:
        """The lineups for this event, if match and available."""
        if isinstance(self._data, ParsedEvent):
            return self._provider.get_event_lineups(self.id)
        return None

    @property
    def incidents(self) -> list[ParsedIncident] | None:
        """The incidents for this event, if match and available."""
        if isinstance(self._data, ParsedEvent):
            return self._provider.get_event_incidents(self.id)
        return None

    @cached_property
    def statistics(self) -> ParsedEventStatisticsResponse | None:
        """The statistics for this event, if match and available."""
        if isinstance(self._data, ParsedEvent):
            return self._provider.get_event_statistics(self.id)
        return None

    @property
    def momentum_graph(self) -> ParsedMomentumGraphResponse | None:
        """The momentum graph for this event, if match and available."""
        if isinstance(self._data, ParsedEvent):
            return self._provider.get_event_graph(self.id)
        return None

    @cached_property
    def h2h(self) -> list[Event] | None:
        """Head-to-head history for the competitors in this event, if match and available."""
        if isinstance(self._data, ParsedEvent):
            return [Event(e) for e in self._provider.get_h2h_history(self.id)]
        return None


    # Race specific properties

    @cached_property
    def substages(self) -> list[Event] | None:
        """The substages for this event, if race and available."""
        if isinstance(self._data, ParsedStage):
            return [Event(s) for s in self._provider.get_stage_substages(self.id)]
        return None

    @property
    def standings(self) -> list[Standings] | None:
        """The standings for this event, if race and available."""
        if isinstance(self._data, ParsedStage):
            competitors_standings = self._provider.get_stage_standings_competitors(self.id)
            teams_standings = self._provider.get_stage_standings_teams(self.id)
            return [
                Standings(competitors_standings, self._provider, name=f"Competitors {self.name}", kind="competitors"),
                Standings(teams_standings, self._provider, name=f"Teams {self.name}", kind="teams")
            ]
        return None


    # Post event properties (available for both matches and races)

    @cached_property
    def winner(self) -> Competitor | None:
        """The winner of this event, if available."""
        if isinstance(self._data, ParsedEvent):
            winner_code = self._data.winnerCode
            if winner_code == 1:
                return Competitor(self._data.home.team, self._provider)
            elif winner_code == 2:
                return Competitor(self._data.away.team, self._provider)
        elif isinstance(self._data, ParsedStage):
            if self._data.winner:
                return Competitor(self._data.winner, self._provider)
        return None

    def _full_load(self) -> None:
        """TODO"""
        if self._full_loaded:
            return
        try:
            if isinstance(self._data, ParsedEvent):
                self._data = replace(self._data, **vars(self._provider.get_event(self.id)))
            elif isinstance(self._data, ParsedStage):
                self._data = replace(self._data, **vars(self._provider.get_stage_details(self.id)))
            assert isinstance(self._data, (ParsedEvent, ParsedStage))
            self._full_loaded = True
            self._clear_cache()
        except Exception:
            logger.exception(f"Failed to fully load event {self.id}.")

    def _clear_cache(self) -> None:
        """Clear cached properties."""
        self.__dict__.pop("season", None)
        self.__dict__.pop("venue", None)
        self.__dict__.pop("competitors", None)
        self.__dict__.pop("score", None)
        self.__dict__.pop("lineups", None)
        self.__dict__.pop("h2h", None)
        self.__dict__.pop("substages", None)


@dataclass
class MatchCompetitors:
    home: Competitor
    away: Competitor

@dataclass
class MatchScore:
    home: int
    away: int
