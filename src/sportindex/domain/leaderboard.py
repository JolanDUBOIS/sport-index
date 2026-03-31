from __future__ import annotations

from functools import cached_property
from datetime import datetime
from pydantic import BaseModel
from typing import TYPE_CHECKING, Any, Optional

from . import logger
from .base import BaseEntity
from .competition import Competition
from .competitor import Competitor
from sportindex.provider.models import (
    _TeamStandingsData, _RacingStandingsEntryData,
    _RankingsResponse, _TeamStandingsEntryData,
    _RankingEntryData, Promotion
)

if TYPE_CHECKING:
    from .core import Sport, Category
    from .gender import Gender
    from sportindex.provider import SofascoreProvider


# =====================================================================
# Standings
# =====================================================================

class Standings(BaseEntity[_TeamStandingsData | list[_RacingStandingsEntryData]]):
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
    _REPR_FIELDS = ("name", "kind", "updated_at")

    def __init__(self, data: _TeamStandingsData | list[_RacingStandingsEntryData], provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not (isinstance(data, _TeamStandingsData) or (isinstance(data, list) and all(isinstance(e, _RacingStandingsEntryData) for e in data))):
            raise TypeError(f"Standings data must be either _TeamStandingsData or list[_RacingStandingsEntryData], got {type(data)}")

    @property
    def name(self) -> Optional[str]:
        """The name of the standings, e.g. "Ligue 1 table", "Formula 1 driver standings", etc."""
        if isinstance(self._data, _TeamStandingsData):
            return self._data.name
        else:
            return self._kwargs.get("name", None)

    @property
    def kind(self) -> Optional[str]:
        """The kind of standings, e.g. "home", "away", "total" (match standings) or "competitors", "teams" (racing standings)."""
        if isinstance(self._data, _TeamStandingsData):
            return self._data.type_
        else:
            return self._kwargs.get("kind", None)

    @property
    def updated_at(self) -> Optional[datetime]:
        """The date and time when the standings were last updated."""
        if isinstance(self._data, _TeamStandingsData):
            return self._data.updated_at
        else:
            return self._data[0].updated_at if self._data else None

    @cached_property
    def sport(self) -> Optional[Sport]:
        """The sport these standings belong to."""
        if self.entries:
            return self.entries[0].competitor.sport
        else:
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
    points: Optional[float] = None

    # Match standings
    matches: Optional[int] = None
    wins: Optional[int] = None
    draws: Optional[int] = None
    losses: Optional[int] = None
    scores_for: Optional[int] = None
    scores_against: Optional[int] = None
    score_formatted: Optional[str] = None
    games_behind: Optional[float] = None  # Kept as float to preserve half-games (e.g. 1.5)
    promotion: Optional[Promotion] = None

    # Racing standings (motorsport)
    victories: Optional[int] = None
    podiums: Optional[int] = None
    races_with_points: Optional[int] = None
    races_started: Optional[int] = None

    # Racing standings (cycling)
    time: Optional[str] = None
    gap_to_leader: Optional[str] = None

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
            
        elif isinstance(raw, _RacingStandingsEntryData):
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


# =====================================================================
# Rankings
# =====================================================================

class Rankings(BaseEntity[_RankingsResponse]):
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
    _REPR_FIELDS = ("id", "name", "slug", "sport", "category", "gender", "updated_at")

    def __init__(self, data: _RankingsResponse, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _RankingsResponse):
            raise TypeError(f"Rankings data must be _RankingsResponse, got {type(data)}")

    @property
    def id(self) -> Optional[int]:
        """The unique ID of these rankings."""
        return self._data.ranking_type.id if self._data.ranking_type else None

    @property
    def name(self) -> Optional[str]:
        """The name of the rankings, e.g. "FIFA Rankings", "ATP Rankings", etc."""
        return self._data.ranking_type.name if self._data.ranking_type else None

    @property
    def slug(self) -> Optional[str]:
        """The slug of the rankings, e.g. "fifa", "atp", etc."""
        return self._data.ranking_type.slug if self._data.ranking_type else None

    @property
    def updated_at(self) -> Optional[datetime]:
        """The date and time when the rankings were last updated."""
        return self._data.ranking_type.last_updated if self._data.ranking_type else None

    @cached_property
    def gender(self) -> Optional[Gender]:
        """The gender category of these rankings, e.g. "M", "F" or "X" (mixed/other)."""
        from .core import Gender
        return Gender(self._data.ranking_type.gender) if self._data.ranking_type and self._data.ranking_type.gender else None

    @cached_property
    def entries(self) -> list[RankingsEntry]:
        """The entries in the rankings."""
        return [RankingsEntry._from_base_schema(e, self._provider) for e in self._data.ranking_rows]

    @cached_property
    def sport(self) -> Optional[Sport]:
        """The sport these rankings belong to."""
        from .core import Sport
        return Sport(self._data.ranking_type.sport, self._provider) if self._data.ranking_type and self._data.ranking_type.sport else None

    @cached_property
    def category(self) -> Optional[Category]:
        """The category these rankings belong to, if any."""
        from .core import Category
        try:
            return Category(self._data.ranking_type.category, self._provider) if self._data.ranking_type and self._data.ranking_type.category else None
        except TypeError:
            return None

    @cached_property
    def competition(self) -> Optional[Competition]:
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
    points: Optional[float] = None

    previous_position: Optional[int] = None
    previous_points: Optional[float] = None
    best_position: Optional[int] = None

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
