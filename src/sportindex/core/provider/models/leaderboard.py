from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from .event import Event
    from .main import Country, Sport, Category
    from .primitives import Timestamp, Promotion
    from .team import Team
    from .tournament import Tournament, UniqueTournament


# =====================================================================
# Leaderboard — Team / Individual Standings
# =====================================================================

class TeamStandingsEntry(TypedDict, total=False):
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
    promotion: Promotion
    gamesBehind: int
    streak: int
    team: Team


class TeamStandings(TypedDict, total=False):
    id: int
    name: str                  # e.g. "Premier League"
    type: str                  # "home", "away", "total"
    rows: list[TeamStandingsEntry]
    tournament: Tournament
    updatedAtTimestamp: Timestamp


# =====================================================================
# Leaderboard — Racing Standings
# =====================================================================

class RacingStandingsEntry(TypedDict, total=False):
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
    team: Team              # Driver/Cyclist or Team/Constructor
    parentTeam: Team        # Team/Constructor if team is Driver/Cyclist, else None
    updatedAtTimestamp: Timestamp


# =====================================================================
# Leaderboard — Rankings
# =====================================================================

class RankingType(TypedDict, total=False):
    id: int
    slug: str
    name: str
    gender: str
    sport: Sport
    category: Category
    uniqueTournament: UniqueTournament
    lastUpdatedTimestamp: Timestamp


class RankingEntry(TypedDict, total=False):
    id: int
    name: str
    position: int         # For MMA, position starts at 0 instead of 1
    points: float
    country: Country
    bestPosition: int
    previousPosition: int
    previousPoints: float
    tournamentsPlayed: int
    team: Team
    lastEvent: Event
    updatedAtTimestamp: Timestamp
