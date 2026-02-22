"""
Entity TypedDict types: tournaments, teams, players, managers, referees, venues.

See __init__.py for full package docstring and conventions.
"""

from __future__ import annotations

from typing import Any, TypedDict

from .common import (
    RawAmount,
    RawCategory,
    RawCoordinates,
    RawCountry,
    RawSport,
    RawStadium,
)


# =====================================================================
# Tournament
# =====================================================================

class RawSeason(TypedDict, total=False):
    id: int
    name: str
    year: str              # e.g. "24/25" or "2025"
    startDateTimestamp: int # Unix timestamp
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
    yearOfFoundation: int
    country: RawCountry
    upperDivisions: list[RawUniqueTournament]
    lowerDivisions: list[RawUniqueTournament]
    titleHolder: RawTeam
    mostTitlesTeams: list[RawTeam]
    linkedUniqueTournaments: list[RawUniqueTournament]
    # REMARK: There are likely more fields (numberOfCompetitors,
    # numberOfDivisions, owner, etc.) that haven't been discovered yet.


class RawTournament(TypedDict, total=False):
    """A Tournament is a concrete instance within a UniqueTournament (e.g. a group)."""
    id: int
    slug: str
    name: str
    category: RawCategory
    uniqueTournament: RawUniqueTournament


class RawUniqueTournamentSeasons(TypedDict, total=False):
    """Wrapper returned by team/player/manager seasons endpoints."""
    uniqueTournament: RawUniqueTournament
    seasons: list[RawSeason]


# =====================================================================
# Participants
# =====================================================================

class RawPerformance(TypedDict, total=False):
    """Manager performance stats."""
    total: int
    wins: int
    draws: int
    losses: int
    goalScored: int
    goalConceded: int
    totalPoints: int


class RawPlayerTeamInfo(TypedDict, total=False):
    """Extra info present on a Team when that team represents an individual
    athlete (tennis, MMA, etc.)."""
    id: int
    residence: str
    birthplace: str
    height: float        # in meters — ASSUMPTION: could be cm in some sports
    weight: float        # in kg
    handedness: str      # e.g. "right-handed"
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
    nameCode: str                                 # e.g. "PSG", "BAR"
    national: bool
    disabled: bool
    gender: str                                   # "M", "F"
    country: RawCountry
    sport: RawSport
    category: RawCategory
    primaryUniqueTournament: RawUniqueTournament
    manager: RawManager                           # forward ref — defined below
    parentTeam: RawTeam                           # self-referential (e.g. B-team → A-team)
    venue: RawVenue                               # forward ref — defined below
    ranking: int
    foundationDateTimestamp: int
    playerTeamInfo: RawPlayerTeamInfo
    # REMARK: MMA teams may have `wdlRecords`


class RawPlayer(TypedDict, total=False):
    id: int
    slug: str
    name: str
    shortName: str
    gender: str          # "M", "F", "X" — ASSUMPTION: "X" exists
    shirtNumber: int
    team: RawTeam
    # Position fields are at the top level of the player dict, not nested
    position: str        # e.g. "G", "D", "M", "F"
    primaryPosition: str # ASSUMPTION: always same as position? unclear
    positionsDetailed: list[str]
    country: RawCountry
    weight: int          # ASSUMPTION: in kg
    height: int          # ASSUMPTION: in cm
    dateOfBirthTimestamp: int
    status: str          # ASSUMPTION: e.g. "active", "injured"?
    retired: bool
    deceased: bool
    proposedMarketValueRaw: RawAmount
    salaryRaw: RawAmount
    handedness: str      # Relevant for racket sports
    preferredFoot: str   # Relevant for football


class RawManager(TypedDict, total=False):
    id: int
    slug: str
    name: str
    shortName: str
    team: RawTeam
    teams: list[RawTeam]
    sport: RawSport
    country: RawCountry
    nationality: str             # REMARK: this is an alpha3 code that the current
                                 #   code merges into the Country object — it's a
                                 #   separate API key from `country`
    deceased: bool
    dateOfBirthTimestamp: int
    performance: RawPerformance
    preferredFormation: str       # e.g. "4-3-3"
    formerPlayerId: int           # ASSUMPTION: int, links to a player ID


class RawReferee(TypedDict, total=False):
    id: int
    slug: str
    name: str
    games: int
    sport: RawSport
    country: RawCountry
    # Card stats are at the top level, not nested
    yellowCards: int
    redCards: int
    yellowRedCards: int


class RawPlayerPreviousTeam(TypedDict, total=False):
    player: RawPlayer
    previousTeam: RawTeam
    transferDate: str  # ISO date string — ASSUMPTION: could be timestamp


class RawTeamPlayers(TypedDict, total=False):
    """Response from /team/{id}/players."""
    players: list[RawPlayer]
    foreignPlayers: list[RawPlayer]
    nationalPlayers: list[RawPlayer]
    playerPreviousTeams: list[RawPlayerPreviousTeam]


class RawTeamSeasonStats(TypedDict, total=False):
    """Response from /team/{id}/unique-tournament/{utId}/season/{sId}/statistics/overall.

    The interesting data is inside the ``statistics`` key, which itself contains
    an ``id``, a ``statisticsType``, and then dozens of dynamic stat keys
    (goals, assists, cleanSheets, etc.) that vary by sport.

    REMARK: The current models flatten this by removing meta keys. Consider
    whether the higher layer should do this or just pass the raw dict through.
    """
    statistics: dict[str, Any] # TODO


# =====================================================================
# Venue
# =====================================================================

class RawVenue(TypedDict, total=False):
    id: int
    slug: str
    name: str
    capacity: int
    city: str
    stadium: RawStadium              # REMARK: Not 100% sure this is always present
    country: RawCountry
    coordinates: RawCoordinates
    mainTeams: list[RawTeam]
