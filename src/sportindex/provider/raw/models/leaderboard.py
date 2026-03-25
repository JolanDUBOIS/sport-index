from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from .event import RawEvent
    from .core import RawCountry, RawSport, RawCategory
    from .primitives import Timestamp, RawPromotion
    from .team import RawTeam
    from .tournament import RawTournament, RawUniqueTournament


# =====================================================================
# Leaderboard — Team / Individual Standings
# =====================================================================

class RawTeamStandingsEntry(TypedDict, total=False):
    id: int
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
    team: RawTeam


class RawTeamStandings(TypedDict, total=False):
    id: int
    name: str                  # e.g. "Premier League"
    type: str                  # "home", "away", "total"
    rows: list[RawTeamStandingsEntry]
    tournament: RawTournament
    updatedAtTimestamp: Timestamp


# =====================================================================
# Leaderboard — Racing Standings
# =====================================================================

class RawRacingStandingsEntry(TypedDict, total=False):
    startNumber: int           # Driver or cyclist number
    number: int                # alternative numbering, if API provides

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
    team: RawTeam              # Driver/Cyclist or Team/Constructor
    parentTeam: RawTeam        # Team/Constructor if team is Driver/Cyclist, else None
    updatedAtTimestamp: Timestamp


# =====================================================================
# Leaderboard — Rankings
# =====================================================================

class RawRankingType(TypedDict, total=False):
    id: int
    slug: str
    name: str
    gender: str
    sport: RawSport
    category: RawCategory
    uniqueTournament: RawUniqueTournament
    lastUpdatedTimestamp: Timestamp


class RawRankingEntry(TypedDict, total=False):
    id: int
    name: str
    position: int         # For MMA, position starts at 0 instead of 1
    points: float
    country: RawCountry

    bestPosition: int
    previousPosition: int
    previousPoints: float

    # Specific to a team or a competitor ranking
    tournamentsPlayed: int
    team: RawTeam
    lastEvent: RawEvent

    # Specific to a country ranking (e.g. UEFA football rankings)
    uniqueTournament: RawUniqueTournament
    playingTeams: int
    totalTeams: int

    updatedAtTimestamp: Timestamp
