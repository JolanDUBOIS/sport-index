"""
Entity dataclass types: tournaments, teams, players, managers, referees, venues.

See __init__.py for full package docstring and conventions.
"""

from __future__ import annotations

from .base import RawModel
from .common import (
    RawCategory,
    RawCountry,
    RawSport,
)
from .primitives import (
    Timestamp,
    RawAmount,
    RawCoordinates,
    RawPerformance,
)


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


# =====================================================================
# Team
# =====================================================================

class RawPlayerTeamInfo(RawModel):
    """Extra info present on a Team when that team represents an individual
    athlete (tennis, MMA, etc.)."""
    id: int
    residence: str
    birthplace: str
    height: float        # in m (e.g. 1.85)
    weight: float        # in kg
    number: int
    plays: str           # e.g. "right-handed"
    mainDriver: bool
    turnedPro: str       # e.g. "2018"
    prizeCurrentRaw: RawAmount
    prizeTotalRaw: RawAmount
    birthDateTimestamp: Timestamp
    currentRanking: int


class RawTeam(RawModel):
    id: int
    slug: str
    name: str
    shortName: str
    fullName: str
    nameCode: str        # e.g. "PSG", "BAR"
    gender: str          # "M", "F"
    sport: RawSport
    category: RawCategory
    country: RawCountry
    tournament: RawTournament
    primaryUniqueTournament: RawUniqueTournament
    national: bool
    disabled: bool
    manager: RawManager
    venue: RawVenue
    foundationDateTimestamp: Timestamp
    ranking: int
    parentTeam: RawTeam
    playerTeamInfo: RawPlayerTeamInfo


# =====================================================================
# Player
# =====================================================================

class RawPlayer(RawModel):
    id: int
    slug: str
    name: str
    firstName: str
    lastName: str
    shortName: str
    team: RawTeam
    gender: str                  # "M", "F", "X"
    dateOfBirthTimestamp: Timestamp
    country: RawCountry
    weight: int                  # in kg
    height: int                  # in cm
    shirtNumber: int
    status: str                  # e.g. "Active", "Retired"
    retired: bool
    deceased: bool
    preferredFoot: str
    salaryRaw: RawAmount
    proposedMarketValueRaw: RawAmount
    contractUntilTimestamp: Timestamp
    position: str                # e.g. "G", "D", "M", "F"
    positionsDetailed: list[str] # e.g. ["RW", "ST"]
    primaryPosition: str


# =====================================================================
# Manager
# =====================================================================

class RawManager(RawModel):
    id: int
    slug: str
    name: str
    shortName: str
    team: RawTeam
    teams: list[RawTeam]
    sport: RawSport
    country: RawCountry
    nationality: str              # ISO3
    nationalityISO2: str          # ISO2
    deceased: bool
    dateOfBirthTimestamp: Timestamp
    performance: RawPerformance
    preferredFormation: str       # e.g. "4-3-3"
    formerPlayerId: int


# =====================================================================
# Referee
# =====================================================================

class RawReferee(RawModel):
    id: int
    slug: str
    name: str
    games: int
    sport: RawSport
    country: RawCountry
    yellowCards: int
    redCards: int
    yellowRedCards: int
    dateOfBirthTimestamp: Timestamp


# =====================================================================
# Venue
# =====================================================================

class RawStadium(RawModel):
    name: str
    capacity: int


class RawCity(RawModel):
    name: str


class RawVenue(RawModel):
    id: int
    slug: str
    name: str
    capacity: int
    city: RawCity
    stadium: RawStadium
    country: RawCountry
    venueCoordinates: RawCoordinates
    mainTeams: list[RawTeam]
