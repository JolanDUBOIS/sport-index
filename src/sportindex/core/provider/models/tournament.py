from __future__ import annotations

from typing import TYPE_CHECKING

from .base import RawModel

if TYPE_CHECKING:
    from .common import RawCategory
    from .entities import RawTeam
    from .primitives import Timestamp


# =====================================================================
# Tournament
# =====================================================================

class RawSeason(RawModel):
    id: int
    name: str
    year: str              # e.g. "24/25" or "2025"
    startDateTimestamp: Timestamp
    description: str


class RawUniqueTournament(RawModel):
    id: int
    slug: str
    name: str
    category: RawCategory
    gender: str
    tier: str
    startDateTimestamp: Timestamp
    endDateTimestamp: Timestamp
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


class RawTournament(RawModel):
    """A Tournament is a concrete instance within a UniqueTournament (e.g. a group)."""
    id: int
    slug: str
    name: str
    category: RawCategory
    uniqueTournament: RawUniqueTournament
