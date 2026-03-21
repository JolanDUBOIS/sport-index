from __future__ import annotations

from functools import cached_property
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from . import logger
from .base import BaseEntity
from sportindex.core.provider.parsed import (
    ParsedTeamStandings, ParsedRacingStandingsEntry, ParsedRankingsResponse
)

if TYPE_CHECKING:
    from .core import Gender, Sport, Category
    from .competition import Competition
    from .competitor import Competitor
    from sportindex.core.provider.parsed import (
        ParsedSofascoreProvider,
        ParsedTeamStandingsEntry,
        ParsedRankingEntry
    )
    from sportindex.core.provider.raw import Promotion


# =====================================================================
# Standings
# =====================================================================

class Standings(BaseEntity[ParsedTeamStandings | list[ParsedRacingStandingsEntry]]):
    """The standings of a competition, e.g. Ligue 1 table, Formula 1 driver standings, etc."""
    REPR_FIELDS = ("id", "name", "kind", "updated_at")

    def __init__(self, data: ParsedTeamStandings | list[ParsedRacingStandingsEntry], provider: ParsedSofascoreProvider | None = None, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not (isinstance(data, ParsedTeamStandings) or (isinstance(data, list) and all(isinstance(e, ParsedRacingStandingsEntry) for e in data))):
            raise ValueError("Standings data must be either ParsedTeamStandings or list[ParsedRacingStandingsEntry]")

    @property
    def name(self) -> Optional[str]:
        """The name of the standings, e.g. "Ligue 1 table", "Formula 1 driver standings", etc."""
        if isinstance(self._data, ParsedTeamStandings):
            return self._data.name
        else:
            return self._kwargs.get("name", None)

    @property
    def kind(self) -> Optional[str]:
        """The kind of standings, e.g. "home", "away", "total" (match standings) or "competitors", "teams" (racing standings)."""
        if isinstance(self._data, ParsedTeamStandings):
            return self._data.type_
        else:
            return self._kwargs.get("kind", None)

    @property
    def updated_at(self) -> Optional[datetime]:
        """The date and time when the standings were last updated."""
        if isinstance(self._data, ParsedTeamStandings):
            return self._data.updatedAt
        else:
            return self._data[0].updatedAt if self._data else None

    @cached_property
    def sport(self) -> Optional[Sport]:
        """The sport these standings belong to."""
        if self.entries:
            return self.entries[0].competitor.sport
        else:
            logger.warning(f"Standings {self.id} has no entries, cannot determine sport")
            return None

    @cached_property
    def entries(self) -> list[StandingsEntry]:
        """The entries in the standings."""
        if isinstance(self._data, ParsedTeamStandings):
            return [StandingsEntry._from_team_standings_entry(e, self._provider) for e in self._data.rows]
        else:
            return [StandingsEntry._from_racing_standings_entry(e, self._provider) for e in self._data]

@dataclass
class StandingsEntry:
    position: int
    competitor: Competitor
    points: int

    # Match standings
    matches: Optional[int] = None
    wins: Optional[int] = None
    draws: Optional[int] = None
    losses: Optional[int] = None
    scores_for: Optional[int] = None
    scores_against: Optional[int] = None
    score_formatted: Optional[str] = None
    games_behind: Optional[int] = None
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
    def _from_team_standings_entry(cls, data: ParsedTeamStandingsEntry, provider: ParsedSofascoreProvider | None = None) -> StandingsEntry:
        from .competitor import Competitor
        return cls(
            position=data.position,
            competitor=Competitor(data.team, provider),
            points=int(data.points),
            matches=int(data.matches),
            wins=int(data.wins),
            draws=int(data.draws),
            losses=int(data.losses),
            scores_for=int(data.scoresFor),
            scores_against=int(data.scoresAgainst),
            score_formatted=data.scoreDiffFormatted,
            games_behind=data.gamesBehind,
            promotion=data.promotion
        )

    @classmethod
    def _from_racing_standings_entry(cls, data: ParsedRacingStandingsEntry, provider: ParsedSofascoreProvider | None = None) -> StandingsEntry:
        from .competitor import Competitor
        return cls(
            position=data.position,
            competitor=Competitor(data.team, provider),
            points=data.points,
            victories=int(data.victories),
            podiums=int(data.podiums),
            races_with_points=int(data.racesWithPoints),
            races_started=int(data.racesStarted),
            time=data.time,
            gap_to_leader=data.gap
        )


# =====================================================================
# Rankings
# =====================================================================

class Rankings(BaseEntity[ParsedRankingsResponse]):
    """The rankings of a sport, e.g. ATP tennis rankings, FIFA football rankings, etc."""
    REPR_FIELDS = ("id", "name", "slug", "sport", "category", "gender", "updated_at")

    def __init__(self, data: ParsedRankingsResponse, provider: ParsedSofascoreProvider | None = None, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

    @property
    def id(self) -> Optional[int]:
        """The unique ID of these rankings."""
        return self._data.rankingType.id if self._data and self._data.rankingType else None

    @property
    def name(self) -> Optional[str]:
        """The name of the rankings, e.g. "FIFA Rankings", "ATP Rankings", etc."""
        return self._data.rankingType.name if self._data and self._data.rankingType else None

    @property
    def slug(self) -> Optional[str]:
        """The slug of the rankings, e.g. "fifa", "atp", etc."""
        return self._data.rankingType.slug if self._data and self._data.rankingType else None

    @property
    def updated_at(self) -> Optional[datetime]:
        """The date and time when the rankings were last updated."""
        return self._data.rankingType.lastUpdated if self._data and self._data.rankingType else None

    @cached_property
    def gender(self) -> Optional[Gender]:
        """The gender category of these rankings, e.g. "M", "F" or "X" (mixed/other)."""
        from .core import Gender
        return Gender(self._data.rankingType.gender) if self._data and self._data.rankingType and self._data.rankingType.gender else None

    @cached_property
    def entries(self) -> list[RankingsEntry]:
        """The entries in the rankings."""
        return [RankingsEntry._from_ranking_entry(e, self._provider) for e in self._data.rankingRows]

    @cached_property
    def sport(self) -> Optional[Sport]:
        """The sport these rankings belong to."""
        from .core import Sport
        return Sport(self._data.rankingType.sport, self._provider) if self._data and self._data.rankingType and self._data.rankingType.sport else None

    @cached_property
    def category(self) -> Optional[Category]:
        """The category these rankings belong to, if any."""
        from .core import Category
        return Category(self._data.rankingType.category, self._provider) if self._data and self._data.rankingType and self._data.rankingType.category else None

    @cached_property
    def competition(self) -> Optional[Competition]:
        """The competition these rankings belong to, if any."""
        from .competition import Competition
        raise NotImplementedError


@dataclass
class RankingsEntry:
    position: int
    entity: Competitor | Competition
    points: int

    previous_position: Optional[int] = None
    previous_points: Optional[int] = None
    best_position: Optional[int] = None

    @classmethod
    def _from_ranking_entry(cls, data: ParsedRankingEntry, provider: ParsedSofascoreProvider | None = None) -> RankingsEntry:
        from .competitor import Competitor
        from .competition import Competition
        entity = Competitor(data.team, provider) if data.team else Competition(data.uniqueTournament, provider) if data.uniqueTournament else None
        if not entity:
            raise ValueError(f"Ranking entry {data.id} has neither team nor unique tournament, cannot determine entity")
        return cls(
            position=data.position,
            entity=entity,
            points=int(data.points),
            previous_position=int(data.previousPosition) if data.previousPosition is not None else None,
            previous_points=int(data.previousPoints) if data.previousPoints is not None else None,
            best_position=int(data.bestPosition) if data.bestPosition is not None else None
        )
