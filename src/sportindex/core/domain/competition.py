"""
Competition domain entity.

A Competition wraps either a UniqueTournament (most sports) or a
UniqueStage (motorsport, cycling). It provides lazy access to
details, seasons, and the parent category.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional, Literal, TYPE_CHECKING

from .base import BaseEntity

if TYPE_CHECKING:
    from .participant import Competitor
    from .season import Season

logger = logging.getLogger(__name__)


class Competition(BaseEntity):
    """A competition (league, cup, grand prix series, etc.).

    Constructed via `_from_raw_unique_tournament()` or `_from_raw_unique_stage()`.
    """

    def __init__(
        self,
        *,
        id: int,
        slug: str,
        name: str,
    ) -> None:
        super().__init__()
        self.id = id
        self.slug = slug
        self.name = name

        self._kind: Literal["tournament", "stage"] = "tournament"  # set by classmethods
        self._category: Optional[Category] = None
        self._details: Optional[CompetitionDetails] = None
        self._seasons: Optional[list[Season]] = None

    # -- Constructors -------------------------------------------------- #

    @classmethod
    def _from_raw_unique_tournament(cls, raw: dict) -> Competition:
        """Build from a RawUniqueTournament dict."""
        comp = cls(
            id=raw.get("id", 0),
            slug=raw.get("slug", ""),
            name=raw.get("name", ""),
        )
        comp._kind = "tournament"
        comp._raw = raw

        # Eagerly extract category if present (it's almost always there)
        if "category" in raw and raw["category"]:
            from .core import Category
            comp._category = Category._from_raw(raw["category"])

        return comp

    @classmethod
    def _from_raw_unique_stage(cls, raw: dict) -> Competition:
        """Build from a RawUniqueStage dict."""
        comp = cls(
            id=raw.get("id", 0),
            slug=raw.get("slug", ""),
            name=raw.get("name", ""),
        )
        comp._kind = "stage"
        comp._raw = raw

        if "category" in raw and raw["category"]:
            from .core import Category
            comp._category = Category._from_raw(raw["category"])

        return comp

    # -- Properties ---------------------------------------------------- #

    @property
    def category(self) -> Optional[Category]:
        """The category this competition belongs to (lazy-loaded if needed)."""
        if self._category is None:
            from .core import Category
            raw_cat = self._raw.get("category")
            if not raw_cat and self._kind == "tournament":
                self._load_full()
                raw_cat = self._raw.get("category")
            if raw_cat:
                self._category = Category._from_raw(raw_cat)
        return self._category

    @property
    def details(self) -> Optional[CompetitionDetails]:
        """Extended details — only available for tournaments, not stages."""
        if self._details is not None:
            return self._details
        if self._kind != "tournament":
            return None

        self._load_full()

        from .participant import Competitor

        # Build related competitions/teams from raw data
        upper = [
            Competition._from_raw_unique_tournament(t)
            for t in self._raw.get("upperDivisions", [])
        ]
        lower = [
            Competition._from_raw_unique_tournament(t)
            for t in self._raw.get("lowerDivisions", [])
        ]
        linked = [
            Competition._from_raw_unique_tournament(c)
            for c in self._raw.get("linkedUniqueTournaments", [])
        ]

        title_holder = None
        if self._raw.get("titleHolder"):
            title_holder = Competitor._from_raw_team(self._raw["titleHolder"])

        most_titles = [
            Competitor._from_raw_team(t)
            for t in self._raw.get("mostTitlesTeams", [])
        ]

        self._details = CompetitionDetails(
            gender=self._raw.get("gender"),
            tier=self._raw.get("tier"),
            founded=self._raw.get("yearOfFoundation"),
            upper_divisions=tuple(upper),
            lower_divisions=tuple(lower),
            title_holder=title_holder,
            most_titles_teams=tuple(most_titles),
            linked_competitions=tuple(linked),
        )
        return self._details

    @property
    def seasons(self) -> list[Season]:
        """Fetch all seasons for this competition (lazy)."""
        if self._seasons is not None:
            return self._seasons

        from .season import Season

        if self._kind == "tournament":
            logger.debug("Fetching seasons for tournament '%s' (id=%s)", self.name, self.id)
            raw_seasons = self._provider.get_unique_tournament_seasons(str(self.id))
            self._seasons = [
                Season._from_raw_season_tournament(s, competition=self)
                for s in raw_seasons
            ]
        else:
            logger.debug("Fetching seasons for stage '%s' (id=%s)", self.name, self.id)
            raw_stages = self._provider.get_unique_stage_seasons(str(self.id))
            self._seasons = [
                Season._from_raw_season_stage(s, competition=self)
                for s in raw_stages
            ]
        return self._seasons

    # -- Internal ------------------------------------------------------ #

    def _load_full(self) -> None:
        if self._full_loaded:
            return
        if self._kind == "tournament":
            logger.debug("Loading full data for tournament '%s' (id=%s)", self.name, self.id)
            self._raw.update(self._provider.get_unique_tournament(str(self.id)))
        # UniqueStage has no dedicated detail endpoint — _raw stays as-is
        self._full_loaded = True


# -- Avoid circular import for type used in this file ------------------ #
from .core import Category  # noqa: E402


@dataclass(frozen=True)
class CompetitionDetails:
    """Extended information about a tournament-type competition."""
    gender: Optional[Literal["M", "F", "X"]]
    tier: Optional[str]
    founded: Optional[int]
    upper_divisions: tuple[Competition, ...]
    lower_divisions: tuple[Competition, ...]
    title_holder: Optional[Competitor]
    most_titles_teams: tuple[Competitor, ...]
    linked_competitions: tuple[Competition, ...]
