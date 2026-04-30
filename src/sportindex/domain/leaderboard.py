from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from sportindex.provider.models import (
    Promotion,
    _RacingStandingsEntryData,
    _RankingEntryData,
    _RankingsResponse,
    _TeamStandingsData,
    _TeamStandingsEntryData,
)

from .base import BaseEntity
from .competition import Competition
from .competitor import Competitor

if TYPE_CHECKING:
    from datetime import datetime

    from sportindex.provider import SofascoreProvider

    from .core import Category, Sport
    from .enums import Gender

logger = logging.getLogger(__name__)


# =====================================================================
# Standings
# =====================================================================

class Standings(BaseEntity):
    """Represents the standings (ranked table) of a competition or sport.

    Can handle both team/match standings (e.g., football league tables) and racing/cycling standings
    (e.g., Formula 1 driver standings).

    Attributes:
        name (str | None): Name of the standings, e.g., "Ligue 1 table".
        kind (str | None): Type of standings, e.g., "home", "away", "competitors", "teams".
        updated_at (datetime | None): Last update timestamp.
        sport (Sport | None): Sport associated with these standings.
        entries (list[StandingsEntry]): Ordered list of entries in the standings.
    """
    _data: _TeamStandingsData | list[_RacingStandingsEntryData]
    _REPR_FIELDS = ("name", "kind", "updated_at")

    def __init__(self, data: _TeamStandingsData | list[_RacingStandingsEntryData], provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not (isinstance(data, _TeamStandingsData) or (isinstance(data, list) and all(isinstance(e, _RacingStandingsEntryData) for e in data))):
            raise TypeError(f"Standings data must be either _TeamStandingsData or list[_RacingStandingsEntryData], got {type(data)}")

    @property
    def name(self) -> str | None:
        """The name of the standings, e.g. "Ligue 1 table", "Formula 1 driver standings", etc."""
        if isinstance(self._data, _TeamStandingsData):
            return self._data.name
        return self._kwargs.get("name", None)

    @property
    def kind(self) -> str | None:
        """The kind of standings, e.g. "home", "away", "total" (match standings) or "competitors", "teams" (racing standings)."""
        if isinstance(self._data, _TeamStandingsData):
            return self._data.type_
        return self._kwargs.get("kind", None)

    @property
    def updated_at(self) -> datetime | None:
        """The date and time when the standings were last updated."""
        if isinstance(self._data, _TeamStandingsData):
            return self._data.updated_at
        return self._data[0].updated_at if self._data else None

    @cached_property
    def sport(self) -> Sport | None:
        """The sport these standings belong to."""
        if self.entries:
            return self.entries[0].competitor.sport
        logger.warning(f"Standings {self.name} has no entries, cannot determine sport")
        return None

    @cached_property
    def entries(self) -> list[StandingsEntry]:
        """The entries in the standings."""
        entries = self._data.rows if isinstance(self._data, _TeamStandingsData) else self._data
        return [StandingsEntry._from_base_schema(e, self._provider) for e in entries]


class StandingsEntry(BaseModel):
    """A single entry in a Standings table.

    Attributes:
        competitor (Competitor): Competitor (team, driver, or rider).
        position (int): Rank/position in the standings.
        points (float): Points accumulated.
        matches, wins, draws, losses, scores_for, scores_against, score_formatted, games_behind, promotion:
            Match-specific fields.
        victories, podiums, races_with_points, races_started:
            Racing-specific fields.
        time, gap_to_leader:
            Cycling-specific fields.
    """
    competitor: Competitor
    position: int
    points: float | None = None

    # Match standings
    matches: int | None = None
    wins: int | None = None
    draws: int | None = None
    losses: int | None = None
    scores_for: int | None = None
    scores_against: int | None = None
    score_formatted: str | None = None
    games_behind: float | None = None  # Kept as float to preserve half-games (e.g. 1.5)
    promotion: Promotion | None = None

    # Racing standings (motorsport)
    victories: int | None = None
    podiums: int | None = None
    races_with_points: int | None = None
    races_started: int | None = None

    # Racing standings (cycling)
    time: str | None = None
    gap_to_leader: str | None = None

    @classmethod
    def _from_base_schema(
        cls,
        raw: _TeamStandingsEntryData | _RacingStandingsEntryData,
        provider: Any
    ) -> StandingsEntry:

        if not raw.team:
            raise ValueError("Standings entry must have an associated team to determine competitor")
        if not raw.position:
            raise ValueError("Standings entry must have a position")

        if isinstance(raw, _TeamStandingsEntryData):
            return cls(
                competitor=Competitor(raw.team, provider),
                position=raw.position,
                points=raw.points,
                matches=raw.matches,
                wins=raw.wins,
                draws=raw.draws,
                losses=raw.losses,
                scores_for=raw.scores_for,
                scores_against=raw.scores_against,
                score_formatted=raw.score_diff_formatted,
                games_behind=raw.games_behind,
                promotion=raw.promotion
            )
        if isinstance(raw, _RacingStandingsEntryData):
            return cls(
                competitor=Competitor(raw.team, provider),
                position=raw.position,
                points=raw.points,
                victories=raw.victories,
                podiums=raw.podiums,
                races_with_points=raw.races_with_points,
                races_started=raw.races_started,
                time=raw.time,
                gap_to_leader=raw.gap
            )
        raise TypeError(
            f"Invalid raw data type: {type(raw).__name__}. "
            f"Expected _TeamStandingsEntryData or _RacingStandingsEntryData."
        )


# =====================================================================
# Rankings
# =====================================================================

class Rankings(BaseEntity):
    """Represents the rankings of a sport, e.g., FIFA, ATP, or Olympic rankings.

    Attributes:
        id (int | None): Unique ID of the ranking type.
        name (str | None): Name of the rankings.
        slug (str | None): URL-friendly slug of the ranking.
        updated_at (datetime | None): Last updated timestamp.
        gender (Gender | None): Gender category of the ranking (M/F/X).
        sport (Sport | None): Sport associated with the ranking.
        category (Category | None): Category, if applicable.
        competition (Competition | None): Competition associated, if applicable.
        entries (list[RankingsEntry]): Ordered list of ranking entries.
    """
    _data: _RankingsResponse
    _REPR_FIELDS = ("id", "name", "slug", "sport", "category", "gender", "updated_at")

    def __init__(self, data: _RankingsResponse, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _RankingsResponse):
            raise TypeError(f"Rankings data must be _RankingsResponse, got {type(data)}")

    @property
    def id(self) -> int | None:
        """The unique ID of these rankings."""
        return self._data.ranking_type.id if self._data.ranking_type else None

    @property
    def name(self) -> str | None:
        """The name of the rankings, e.g. "FIFA Rankings", "ATP Rankings", etc."""
        return self._data.ranking_type.name if self._data.ranking_type else None

    @property
    def slug(self) -> str | None:
        """The slug of the rankings, e.g. "fifa", "atp", etc."""
        return self._data.ranking_type.slug if self._data.ranking_type else None

    @property
    def updated_at(self) -> datetime | None:
        """The date and time when the rankings were last updated."""
        return self._data.ranking_type.last_updated if self._data.ranking_type else None

    @cached_property
    def gender(self) -> Gender | None:
        """The gender category of these rankings, e.g. "M", "F" or "X" (mixed/other)."""
        from .enums import Gender
        return Gender(self._data.ranking_type.gender) if self._data.ranking_type and self._data.ranking_type.gender else None

    @cached_property
    def entries(self) -> list[RankingsEntry]:
        """The entries in the rankings."""
        return [RankingsEntry._from_base_schema(e, self._provider) for e in self._data.ranking_rows]

    @cached_property
    def sport(self) -> Sport | None:
        """The sport these rankings belong to."""
        from .core import Sport
        return Sport(self._data.ranking_type.sport, self._provider) if self._data.ranking_type and self._data.ranking_type.sport else None

    @cached_property
    def category(self) -> Category | None:
        """The category these rankings belong to, if any."""
        from .core import Category
        try:
            return Category(self._data.ranking_type.category, self._provider) if self._data.ranking_type and self._data.ranking_type.category else None
        except TypeError:
            return None

    @cached_property
    def competition(self) -> Competition | None:
        """The competition these rankings belong to, if any."""
        from .competition import Competition
        try:
            return Competition(self._data.ranking_type.unique_tournament, self._provider) if self._data.ranking_type and self._data.ranking_type.unique_tournament else None
        except TypeError:
            return None


class RankingsEntry(BaseModel):
    """A single entry in a Rankings table.

    Attributes:
        position (int): Current position.
        entity (Competitor | Competition): Entity being ranked.
        points (float): Points in the ranking.
        previous_position (int | None): Previous ranking position.
        previous_points (float | None): Previous points.
        best_position (int | None): Best historical position.
    """
    position: int
    entity: Competitor | Competition
    points: float | None = None

    previous_position: int | None = None
    previous_points: float | None = None
    best_position: int | None = None

    @classmethod
    def _from_base_schema(cls, raw: _RankingEntryData, provider: Any) -> RankingsEntry:
        """Alternative constructor to build a domain RankingsEntry from raw provider data."""

        if raw.unique_tournament:
            entity = Competition(raw.unique_tournament, provider)
        elif raw.team:
            entity = Competitor(raw.team, provider)
        else:
            raise ValueError("Ranking entry must have either a team or a unique tournament associated")

        return cls(
            position=raw.position,
            entity=entity,
            points=raw.points,
            previous_position=raw.previous_position,
            previous_points=raw.previous_points,
            best_position=raw.best_position
        )
