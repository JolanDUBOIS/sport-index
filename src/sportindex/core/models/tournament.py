from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime

from .base import BaseModel, RawModel, ParsedModel
from .common import Category
from .primitives import Timestamp

if TYPE_CHECKING:
    from .team import RawTeam, ParsedTeam


# =====================================================================
# Season
# =====================================================================

class Season(BaseModel):
    id: int
    name: str
    year: str              # e.g. "24/25" or "2025"
    description: str

class RawSeason(Season, RawModel):
    startDateTimestamp: Timestamp

class ParsedSeason(Season, ParsedModel):
    startDateTimestamp: datetime


# =====================================================================
# Unique Tournament
# =====================================================================

class UniqueTournament(BaseModel):
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

class RawUniqueTournament(UniqueTournament, RawModel):
    startDateTimestamp: Timestamp
    endDateTimestamp: Timestamp
    upperDivisions: list[RawUniqueTournament]
    lowerDivisions: list[RawUniqueTournament]
    titleHolder: RawTeam
    mostTitlesTeams: list[RawTeam]
    linkedUniqueTournaments: list[RawUniqueTournament]

class ParsedUniqueTournament(UniqueTournament, ParsedModel):
    startDateTimestamp: datetime
    endDateTimestamp: datetime
    upperDivisions: list[ParsedUniqueTournament]
    lowerDivisions: list[ParsedUniqueTournament]
    titleHolder: ParsedTeam
    mostTitlesTeams: list[ParsedTeam]
    linkedUniqueTournaments: list[ParsedUniqueTournament]


# =====================================================================
# Tournament
# =====================================================================

class Tournament(BaseModel):
    """A Tournament is a concrete instance within a UniqueTournament (e.g. a group)."""
    id: int
    slug: str
    name: str
    category: Category

class RawTournament(Tournament, RawModel):
    uniqueTournament: RawUniqueTournament

class ParsedTournament(Tournament, ParsedModel):
    uniqueTournament: ParsedUniqueTournament
