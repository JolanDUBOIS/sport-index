from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from sportindex.api_client.models import (
    Promotion,
    _RacingStandingsData,
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

    from sportindex.api_client import SofascoreProvider

    from .core import Category, Sport
    from .enums import Gender

logger = logging.getLogger(__name__)


# =====================================================================
# Standings
# =====================================================================

class Standings(BaseEntity):
    """A ranked table within one season or stage — a league table, a drivers' championship.

    Standings come from a `Season` or a `StageEvent` rather than being addressable on their
    own, so they carry no ID. The same class covers league tables and racing championships;
    which fields their entries populate differs, and `kind` tells you which sort you hold.

    Attributes:
        name (str | None): What the table is called, e.g. "Ligue 1", "Teams Monaco Grand Prix".
        kind (str | None): Which cut of the season the table covers — "total", "home" or
            "away" for league tables; "competitors" or "teams" for racing championships.
        updated_at (datetime | None): When the provider last recomputed the table.
        sport (Sport | None): The sport being ranked, taken from the first entry. None for an
            empty table.
        entries (list[StandingsEntry]): The rows, in the provider's order. Rows that cannot be
            represented — a retired driver with no classified position, say — are dropped
            rather than failing the whole table.
        source (_TeamStandingsData | _RacingStandingsData): The parsed payload backing this
            entity. (inherited from BaseEntity)

    Raises:
        TypeError: If constructed with data that is neither `_TeamStandingsData` nor
            `_RacingStandingsData`.
    """
    _data: _TeamStandingsData | _RacingStandingsData
    _REPR_FIELDS = ("name", "kind", "updated_at")

    def __init__(self, data: _TeamStandingsData | _RacingStandingsData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not (isinstance(data, (_TeamStandingsData, _RacingStandingsData))):
            raise TypeError(f"Standings data must be either _TeamStandingsData or _RacingStandingsData, got {type(data)}")

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
        return self._data.standings[0].updated_at if self._data.standings else None

    @cached_property
    def sport(self) -> Sport | None:
        """The sport these standings belong to."""
        if self.entries:
            return self.entries[0].competitor.sport
        logger.warning(f"Standings {self.name} has no entries, cannot determine sport")
        return None

    @cached_property
    def entries(self) -> list[StandingsEntry]:
        """The entries in the standings.

        Entries that can't be represented (e.g. a DNF racer with no classified
        position) are skipped rather than failing the whole standings table.
        """
        entries = self._data.rows if isinstance(self._data, _TeamStandingsData) else self._data.standings
        result = []
        for e in entries:
            try:
                result.append(StandingsEntry._from_base_schema(e, self._provider))
            except ValueError as err:
                logger.debug(f"Skipping standings entry in {self.name}: {err}")
        return result


class StandingsEntry(BaseModel):
    """One row of a `Standings` table.

    Only `competitor` and `position` are always present. The rest divide by table kind:
    league tables populate the match fields, racing championships the motorsport or cycling
    ones. Expect the others to be None.

    Attributes:
        competitor (Competitor): Who the row is about — a team, a driver, a rider.
        position (int): Rank in the table. Starts at 1, except in MMA rankings where the
            champion sits at 0.
        points (float | None): Points accumulated.

        matches (int | None): Games played. League tables.
        wins (int | None): Games won. League tables.
        draws (int | None): Games drawn. League tables.
        losses (int | None): Games lost. League tables.
        scores_for (int | None): Goals or points scored. League tables.
        scores_against (int | None): Goals or points conceded. League tables.
        score_formatted (str | None): Score difference as the provider renders it, e.g. "+15".
            League tables.
        games_behind (float | None): Games behind the leader, halves included. League tables.
        promotion (Promotion | None): What this position qualifies for, e.g. "Champions
            League". League tables.

        victories (int | None): Races won. Motorsport.
        podiums (int | None): Top-three finishes. Motorsport.
        races_with_points (int | None): Races that scored. Motorsport.
        races_started (int | None): Races entered. Motorsport.

        time (str | None): Total elapsed time, as the provider renders it. Cycling.
        gap_to_leader (str | None): Time behind the leader, as the provider renders it. Cycling.
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
    """A sport-wide ranking table that outlives any one season — FIFA, ATP, UFC divisions.

    Unlike `Standings`, which belongs to a season, a ranking is a standing order maintained
    by a governing body. Reached through `Sport.get_rankings()`. Rankings are not addressable
    as entities, so `id` here is the provider's raw ranking-type ID, not an SDK ID.

    Attributes:
        id (int | None): The provider's raw ranking-type ID, e.g. 2 for the FIFA rankings.
            Not an SDK ID.
        name (str | None): What the ranking is called, e.g. "FIFA Rankings".
        slug (str | None): URL-friendly identifier, e.g. "fifa".
        updated_at (datetime | None): When the ranking was last published.
        gender (Gender | None): Which gender's ranking this is — MALE, FEMALE or UNSPECIFIED.
        sport (Sport | None): The sport being ranked, if the provider states it.
        category (Category | None): The category the ranking is scoped to, if any.
        competition (Competition | None): The competition the ranking is scoped to, if any.
        entries (list[RankingsEntry]): The rows, in the provider's order.
        source (_RankingsResponse): The parsed payload backing this entity.
            (inherited from BaseEntity)

    Raises:
        TypeError: If constructed with data that is not `_RankingsResponse`.
        ValueError: If a row names neither a team nor a competition to rank.
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
    """One row of a `Rankings` table.

    Attributes:
        position (int): Current rank. Starts at 1, except in MMA rankings where the champion
            sits at 0.
        entity (Competitor | Competition): What is ranked — usually a team or athlete, but a
            competition in rankings that order tournaments.
        points (float | None): Ranking points held.
        previous_position (int | None): Rank at the previous publication.
        previous_points (float | None): Points at the previous publication.
        best_position (int | None): Best rank ever reached.
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
