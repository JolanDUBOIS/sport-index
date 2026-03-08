from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from .main import Category
    from .primitives import Timestamp
    from .team import Team


# =====================================================================
# Season
# =====================================================================

class Season(TypedDict, total=False):
    id: int
    name: str
    year: str              # e.g. "24/25" or "2025"
    description: str
    startDateTimestamp: Timestamp


# =====================================================================
# Unique Tournament
# =====================================================================

class UniqueTournament(TypedDict, total=False):
    id: int
    slug: str
    name: str
    category: Category
    gender: str
    tier: str
    titleHolderTitles: int
    mostTitles: int
    hasRounds: bool
    hasGroups: bool
    hasPlayoffSeries: bool
    groundType: str         # e.g. "Red clay", "Grass", etc.
    numberOfSets: int
    tennisPoints: int
    startDateTimestamp: Timestamp
    endDateTimestamp: Timestamp
    upperDivisions: list[UniqueTournament]
    lowerDivisions: list[UniqueTournament]
    titleHolder: Team
    mostTitlesTeams: list[Team]
    linkedUniqueTournaments: list[UniqueTournament]


# =====================================================================
# Tournament
# =====================================================================

class Tournament(TypedDict, total=False):
    """A Tournament is a concrete instance within a UniqueTournament (e.g. a group)."""
    id: int
    slug: str
    name: str
    category: Category
    uniqueTournament: UniqueTournament
