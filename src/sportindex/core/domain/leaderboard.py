"""
Leaderboard domain entities: Standings, Rankings, and their entries.

Standings come from tournament seasons (Premier League table, NBA standings).
Rankings come from the ranking system (FIFA rankings, ATP rankings).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional, Literal, TYPE_CHECKING

from .base import BaseEntity
from .values import Promotion, _promotion_from_raw

if TYPE_CHECKING:
    from .core import Sport, Category, Country
    from .participant import Competitor

logger = logging.getLogger(__name__)


# =====================================================================
# Standings (tournament season tables)
# =====================================================================

class Standings(BaseEntity):
    """A standings table (e.g. Premier League table, NBA Western Conference)."""

    def __init__(
        self,
        *,
        id: int,
        name: str,
    ) -> None:
        super().__init__()
        self.id = id
        self.name = name
        self._view: Optional[str] = None       # "total"/"home"/"away" (match) or "competitors"/"teams" (racing)
        self._basis: Literal["match", "racing"] = "match"

        self._entries: Optional[list[StandingsEntry]] = None

    @classmethod
    def _from_raw(cls, raw: dict) -> Standings:
        """Build from a RawTeamStandings dict."""
        standings = cls(
            id=raw.get("id", 0),
            name=raw.get("name", ""),
        )
        standings._view = raw.get("type")
        standings._basis = "match"
        standings._raw = raw
        return standings

    @property
    def entries(self) -> list[StandingsEntry]:
        """Standings rows (lazy — parsed on first access)."""
        if self._entries is not None:
            return self._entries

        from .participant import Competitor

        rows = self._raw.get("rows", [])
        self._entries = [
            StandingsEntry._from_raw(row)
            for row in rows
        ]
        logger.debug("Parsed %d standings entries for '%s'", len(self._entries), self.name)
        return self._entries


@dataclass(frozen=True)
class StandingsEntry:
    """A single row in a standings table."""

    position: int
    points: Optional[int] = None
    competitor: Optional[Competitor] = None

    # Match-based stats (football, basketball, etc.)
    matches: Optional[int] = None
    wins: Optional[int] = None
    draws: Optional[int] = None
    losses: Optional[int] = None
    scores_for: Optional[int] = None
    scores_against: Optional[int] = None
    score_difference: Optional[str] = None
    promotion: Optional[Promotion] = None
    games_behind: Optional[int] = None
    streak: Optional[int] = None
    percentage: Optional[float] = None

    # Racing stats (motorsport)
    time: Optional[str] = None
    interval: Optional[str] = None
    gap: Optional[str] = None
    victories: Optional[int] = None
    races_started: Optional[int] = None
    races_with_points: Optional[int] = None
    pole_positions: Optional[int] = None
    podiums: Optional[int] = None
    fastest_laps: Optional[int] = None

    @classmethod
    def _from_raw(cls, raw: dict) -> StandingsEntry:
        """Build from a RawTeamStandingsEntry or RawRacingStandingsEntry dict."""
        from .participant import Competitor

        competitor = None
        if "team" in raw and raw["team"]:
            competitor = Competitor._from_raw_team(raw["team"])

        return cls(
            position=raw.get("position", 0),
            points=raw.get("points"),
            competitor=competitor,
            # Match-based fields
            matches=raw.get("matches"),
            wins=raw.get("wins"),
            draws=raw.get("draws"),
            losses=raw.get("losses"),
            scores_for=raw.get("scoresFor"),
            scores_against=raw.get("scoresAgainst"),
            score_difference=raw.get("scoreDiffFormatted"),
            promotion=_promotion_from_raw(raw.get("promotion")),
            games_behind=raw.get("gamesBehind"),
            streak=raw.get("streak"),
            percentage=raw.get("percentage"),
            # Racing fields
            time=raw.get("time"),
            interval=raw.get("interval"),
            gap=raw.get("gap"),
            victories=raw.get("victories"),
            races_started=raw.get("racesStarted"),
            races_with_points=raw.get("racesWithPoints"),
            pole_positions=raw.get("polePositions"),
            podiums=raw.get("podiums"),
            fastest_laps=raw.get("fastestLaps"),
        )


# =====================================================================
# Rankings (FIFA, ATP, etc.)
# =====================================================================

class Rankings(BaseEntity):
    """A ranking system (e.g. FIFA World Rankings, ATP Rankings)."""

    def __init__(
        self,
        *,
        id: int,
        name: str,
        gender: Optional[Literal["M", "F", "X"]] = None,
    ) -> None:
        super().__init__()
        self.id = id
        self.name = name
        self.gender = gender

        self._sport: Optional[Sport] = None
        self._category: Optional[Category] = None
        self._entries: Optional[list[RankingsEntry]] = None

    @classmethod
    def _from_raw(cls, raw: dict) -> Rankings:
        """Build from a RawRankingsResponse dict (the full response).

        Expects the top-level dict with `rankingType` and `rankingRows`.
        """
        ranking_type = raw.get("rankingType", {})

        rankings = cls(
            id=ranking_type.get("id", 0),
            name=ranking_type.get("name", ""),
            gender=ranking_type.get("gender"),
        )
        rankings._raw = raw

        from .core import Sport, Category
        if "sport" in ranking_type and ranking_type["sport"]:
            rankings._sport = Sport._from_raw(ranking_type["sport"])
        if "category" in ranking_type and ranking_type["category"]:
            rankings._category = Category._from_raw(ranking_type["category"])

        return rankings

    @property
    def sport(self) -> Optional[Sport]:
        return self._sport

    @property
    def category(self) -> Optional[Category]:
        return self._category

    @property
    def entries(self) -> list[RankingsEntry]:
        """Ranking rows (lazy — parsed on first access)."""
        if self._entries is not None:
            return self._entries

        rows = self._raw.get("rankingRows", [])
        self._entries = [
            RankingsEntry._from_raw(row)
            for row in rows
        ]
        logger.debug("Parsed %d ranking entries for '%s'", len(self._entries), self.name)
        return self._entries


@dataclass(frozen=True)
class RankingsEntry:
    """A single row in a rankings table."""

    position: int
    points: Optional[float] = None
    previous_position: Optional[int] = None
    previous_points: Optional[float] = None
    competitor: Optional[Competitor] = None
    country: Optional[Country] = None

    @classmethod
    def _from_raw(cls, raw: dict) -> RankingsEntry:
        """Build from a RawRankingEntry dict."""
        from .participant import Competitor
        from .core import Country

        competitor = None
        if "team" in raw and raw["team"]:
            competitor = Competitor._from_raw_team(raw["team"])

        country = Country._from_raw(raw.get("country"))

        return cls(
            position=raw.get("position", 0),
            points=raw.get("points"),
            previous_position=raw.get("previousPosition"),
            previous_points=raw.get("previousPoints"),
            competitor=competitor,
            country=country,
        )
