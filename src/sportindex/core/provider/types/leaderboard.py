"""
Leaderboard, ranking, channel, search, and transfer TypedDict types.

See __init__.py for full package docstring and conventions.
"""

from __future__ import annotations

from typing import TypedDict

from .common import RawCategory, RawCountry, RawSport
from .entities import RawTeam, RawTournament, RawUniqueTournament
from .event import RawEvent


# =====================================================================
# Leaderboard — Team / Individual Standings
# =====================================================================

class RawPromotion(TypedDict, total=False):
    id: int
    text: str  # Display name, e.g. "Champions League"


class RawTeamStandingsEntry(TypedDict, total=False):
    id: int
    team: RawTeam
    position: int
    matches: int
    wins: int
    draws: int
    losses: int
    points: int
    percentage: float          # Win percentage
    scoresFor: int
    scoresAgainst: int
    scoreDiffFormatted: str    # e.g. "+15"
    promotion: RawPromotion
    gamesBehind: int
    streak: int


class RawTeamStandings(TypedDict, total=False):
    id: int
    name: str                  # e.g. "Premier League"
    rows: list[RawTeamStandingsEntry]
    tournament: RawTournament
    updatedAtTimestamp: int
    type: str                  # "home", "away", "total"


# =====================================================================
# Leaderboard — Racing Standings
# =====================================================================

class RawRacingStandingsEntry(TypedDict, total=False):
    # Identity / Participant
    team: RawTeam              # Driver/Cyclist or Team/Constructor
    parentTeam: RawTeam        # Team/Constructor if team is Driver/Cyclist, else None
    startNumber: int           # Driver or cyclist number
    number: int                # alternative numbering, if API provides
    updatedAtTimestamp: int

    # Position / Result
    position: int
    points: int
    interval: str              # Interval to competitor ahead
    gap: str                   # Gap to leader
    totalTime: str
    time: str

    # Race-specific stats (Motorsport)
    gridPosition: int
    laps: int
    lapsLed: int
    victories: int
    racesStarted: int
    racesWithPoints: int
    polePositions: int
    podiums: int
    fastestLaps: int
    fastestLapTime: str
    personalFastestLap: int    # Which lap was driver's personal fastest
    personalFastestLapTime: str
    pitStops: int
    tyreType: str
    tyreState: str

    # Cycling-specific
    sprint: int
    climb: int
    sprintPosition: int
    climbPosition: int
    shirt: str


# =====================================================================
# Leaderboard — Rankings
# =====================================================================

class RawRankingType(TypedDict, total=False):
    """Nested under the ``rankingType`` key in ranking responses."""
    id: int
    slug: str
    name: str
    gender: str
    sport: RawSport
    category: RawCategory
    uniqueTournament: RawUniqueTournament
    lastUpdatedTimestamp: int


class RawRankingEntry(TypedDict, total=False):
    id: int
    name: str
    position: int         # For MMA, position starts at 0 instead of 1
    team: RawTeam
    points: float
    country: RawCountry
    bestPosition: int
    previousPosition: int
    previousPoints: float
    tournamentsPlayed: int
    lastEvent: RawEvent
    updatedAtTimestamp: int


class RawRankingsResponse(TypedDict, total=False):
    """Response from /rankings/{id}.
    REMARK: The current code flattens rankingType into top-level fields.
    In this raw approach, access via data["rankingType"]["id"], etc.
    """
    rankingType: RawRankingType
    rankingRows: list[RawRankingEntry]
