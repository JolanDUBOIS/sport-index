from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from .core import RawCategory
    from .primitives import Timestamp
    from .team import RawTeam


# =====================================================================
# Season
# =====================================================================

class RawSeason(TypedDict, total=False):
    id: int
    name: str
    year: str              # e.g. "24/25" or "2025"
    description: str
    startDateTimestamp: Timestamp


# =====================================================================
# Unique Tournament
# =====================================================================

class RawUniqueTournament(TypedDict, total=False):
    id: int
    slug: str
    name: str
    category: RawCategory
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
    upperDivisions: list[RawUniqueTournament]
    lowerDivisions: list[RawUniqueTournament]
    titleHolder: RawTeam
    mostTitlesTeams: list[RawTeam]
    linkedUniqueTournaments: list[RawUniqueTournament]


# =====================================================================
# Tournament
# =====================================================================

class RawTournament(TypedDict, total=False):
    """A Tournament is a concrete instance within a UniqueTournament (e.g. a group)."""
    id: int
    slug: str
    name: str
    category: RawCategory
    uniqueTournament: RawUniqueTournament
