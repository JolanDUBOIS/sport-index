"""
Foundational domain entities: Sport, Country, Category.

These are lightweight — they carry identifying info and provide
navigation to related entities (categories, competitions).
"""

from __future__ import annotations

import logging
from typing import Optional, Literal, TYPE_CHECKING

from .base import BaseEntity

if TYPE_CHECKING:
    from .competition import Competition
    from .leaderboard import Rankings

logger = logging.getLogger(__name__)


# =====================================================================
# Sport
# =====================================================================

class Sport(BaseEntity):
    """A sport (football, tennis, basketball, etc.)."""

    def __init__(
        self,
        *,
        id: int,
        slug: str,
        name: str
    ) -> None:
        super().__init__()
        self.id = id
        self.slug = slug
        self.name = name
        self._categories: Optional[list[Category]] = None
        self._rankings: Optional[list[Rankings]] = None

    @classmethod
    def _from_raw(cls, raw: dict) -> Sport:
        """Build a Sport from a RawSport dict."""
        sport = cls(
            id=raw.get("id"),
            slug=raw.get("slug", ""),
            name=raw.get("name", ""),
        )
        sport._raw = raw
        return sport

    @property
    def categories(self) -> list[Category]:
        """Fetch all categories for this sport (lazy)."""
        if self._categories is None:
            logger.debug("Fetching categories for sport '%s'", self.slug)
            raw_categories = self._provider.get_categories(self.slug)
            self._categories = [
                Category._from_raw(c)
                for c in raw_categories
            ]
        return self._categories

    def rankings(self, *, gender: Literal["M", "F", "X"] | None = None) -> list[Rankings]:
        """Fetch rankings for this sport (lazy, cached).

        Args:
            gender: Filter by ``"M"`` (male), ``"F"`` (female), or ``"X"`` (mixed).
                    ``None`` returns all rankings for the sport.

        Rankings are fetched once and cached.  When *gender* is given,
        only the matching subset is returned (but the full set is still
        cached for future calls without filter).
        """
        if self._rankings is None:
            from .leaderboard import Rankings
            from .static import SPORT_RANKINGS

            entries = SPORT_RANKINGS.get(self.slug, [])
            results: list[Rankings] = []
            for ranking_id, _ in entries:
                logger.debug("Fetching ranking %d for sport '%s'", ranking_id, self.slug)
                raw = self._provider.get_ranking(str(ranking_id))
                results.append(Rankings._from_raw(raw))
            self._rankings = results

        if gender is None:
            return self._rankings
        return [r for r in self._rankings if r.gender == gender]


# ==============================================================
# Country
# =====================================================================

class Country(BaseEntity):
    """A country — used as a geographic anchor for categories, players, etc."""

    def __init__(
        self,
        *,
        name: str,
        slug: str = "",
        alpha2: Optional[str] = None,
        alpha3: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.name = name
        self.slug = slug
        self.alpha2 = alpha2
        self.alpha3 = alpha3

    @classmethod
    def _from_raw(cls, raw: dict | None) -> Optional[Country]:
        """Build a Country from a RawCountry dict. Returns None if raw is empty."""
        if not raw or "name" not in raw:
            return None
        country = cls(
            name=raw["name"],
            slug=raw.get("slug", ""),
            alpha2=raw.get("alpha2"),
            alpha3=raw.get("alpha3"),
        )
        country._raw = raw
        return country

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Country):
            return NotImplemented
        if self.alpha2 and other.alpha2:
            return self.alpha2 == other.alpha2
        return self.name == other.name

    def __hash__(self) -> int:
        if self.alpha2:
            return hash((type(self), self.alpha2))
        return hash((type(self), self.name))


# =====================================================================
# Category
# =====================================================================

class Category(BaseEntity):
    """A category within a sport (e.g. 'England', 'France', 'International').

    Categories group competitions (unique tournaments / unique stages).
    """

    def __init__(
        self,
        *,
        id: int,
        name: str,
        slug: str,
        sport: Optional[Sport] = None,
        country: Optional[Country] = None,
    ) -> None:
        super().__init__()
        self.id = id
        self.name = name
        self.slug = slug
        self._sport = sport
        self._country = country
        self._competitions: Optional[list[Competition]] = None

    @classmethod
    def _from_raw(cls, raw: dict) -> Category:
        """Build a Category from a RawCategory dict."""
        sport = (
            Sport._from_raw(raw["sport"])
            if "sport" in raw and raw["sport"]
            else None
        )
        country = Country._from_raw(raw.get("country"))
        cat = cls(
            id=raw.get("id", 0),
            name=raw.get("name", ""),
            slug=raw.get("slug", ""),
            sport=sport,
            country=country,
        )
        cat._raw = raw
        return cat

    @property
    def sport(self) -> Optional[Sport]:
        return self._sport

    @property
    def country(self) -> Optional[Country]:
        return self._country

    @property
    def competitions(self) -> list[Competition]:
        """Fetch competitions (unique tournaments + unique stages) in this category (lazy)."""
        from .competition import Competition

        if self._competitions is None:
            logger.debug("Fetching competitions for category '%s' (id=%s)", self.name, self.id)
            raw_uts = self._provider.get_category_unique_tournaments(str(self.id))
            raw_stages = self._provider.get_category_unique_stages(str(self.id))
            self._competitions = (
                [Competition._from_raw_unique_tournament(ut) for ut in raw_uts]
                + [Competition._from_raw_unique_stage(s) for s in raw_stages]
            )
        return self._competitions
