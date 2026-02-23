"""
Entity TypedDict types: tournaments, teams, players, managers, referees, venues.

See __init__.py for full package docstring and conventions.
"""

from __future__ import annotations

from typing import TypedDict

from .common import (
    RawCategory,
    RawCountry,
    RawSport,
)
from .primitives import (
    RawAmount,
    RawCoordinates,
    RawPerformance,
)
from .tournament import (
    RawUniqueTournament,
    RawTournament,
)


# =====================================================================
# Team
# =====================================================================

class RawPlayerTeamInfo(TypedDict, total=False):
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
    birthDateTimestamp: int
    currentRanking: int


class RawTeam(TypedDict, total=False):
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
    foundationDateTimestamp: int
    ranking: int
    parentTeam: RawTeam
    playerTeamInfo: RawPlayerTeamInfo


# =====================================================================
# Player
# =====================================================================

class RawPlayer(TypedDict, total=False):
    id: int
    slug: str
    name: str
    firstName: str
    lastName: str
    shortName: str
    team: RawTeam
    gender: str                  # "M", "F", "X"
    dateOfBirthTimestamp: int
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
    contractUntilTimestamp: int
    position: str                # e.g. "G", "D", "M", "F"
    positionsDetailed: list[str] # e.g. ["RW", "ST"]
    primaryPosition: str


# =====================================================================
# Manager
# =====================================================================

class RawManager(TypedDict, total=False):
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
    dateOfBirthTimestamp: int
    performance: RawPerformance
    preferredFormation: str       # e.g. "4-3-3"
    formerPlayerId: int


# =====================================================================
# Referee
# =====================================================================

class RawReferee(TypedDict, total=False):
    id: int
    slug: str
    name: str
    games: int
    sport: RawSport
    country: RawCountry
    yellowCards: int
    redCards: int
    yellowRedCards: int
    dateOfBirthTimestamp: int


# =====================================================================
# Venue
# =====================================================================

class RawStadium(TypedDict, total=False):
    name: str
    capacity: int


class RawCity(TypedDict, total=False):
    name: str


class RawVenue(TypedDict, total=False):
    id: int
    slug: str
    name: str
    capacity: int
    city: RawCity
    stadium: RawStadium
    country: RawCountry
    venueCoordinates: RawCoordinates
    mainTeams: list[RawTeam]
