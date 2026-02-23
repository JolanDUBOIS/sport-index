from __future__ import annotations

from typing import TypedDict

from .common import (
    RawCategory,
    RawCountry,
)
from .entities import (
    RawTeam,
)


# =====================================================================
# Tournament
# =====================================================================

class RawSeason(TypedDict, total=False):
    id: int
    name: str
    year: str              # e.g. "24/25" or "2025"
    startDateTimestamp: int
    description: str


class RawUniqueTournament(TypedDict, total=False):
    id: int
    slug: str
    name: str
    category: RawCategory
    gender: str
    tier: str
    startDateTimestamp: int
    endDateTimestamp: int
    upperDivisions: list[RawUniqueTournament]
    lowerDivisions: list[RawUniqueTournament]
    titleHolder: RawTeam
    titleHolderTitles: int
    mostTitlesTeams: list[RawTeam]
    mostTitles: int
    linkedUniqueTournaments: list[RawUniqueTournament]
    hasRounds: bool
    hasGroups: bool
    hasPlayoffSeries: bool
    groundType: str         # e.g. "Red clay", "Grass", etc.
    numberOfSets: int
    tennisPoints: int


class RawTournament(TypedDict, total=False):
    """A Tournament is a concrete instance within a UniqueTournament (e.g. a group)."""
    id: int
    slug: str
    name: str
    category: RawCategory
    uniqueTournament: RawUniqueTournament
