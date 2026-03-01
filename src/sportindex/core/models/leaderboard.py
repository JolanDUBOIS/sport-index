from datetime import datetime

from .base import BaseModel, RawModel, ParsedModel
from .common import Country, Sport, Category
from .event import RawEvent, ParsedEvent
from .primitives import Timestamp, Promotion
from .team import RawTeam, ParsedTeam
from .tournament import RawTournament, ParsedTournament, RawUniqueTournament, ParsedUniqueTournament

# =====================================================================
# Leaderboard — Team / Individual Standings
# =====================================================================


class TeamStandingsEntry(BaseModel):
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

class RawTeamStandingsEntry(TeamStandingsEntry, RawModel):
    team: RawTeam

class ParsedTeamStandingsEntry(TeamStandingsEntry, ParsedModel):
    team: ParsedTeam


class TeamStandings(BaseModel):
    id: int
    name: str                  # e.g. "Premier League"
    type: str                  # "home", "away", "total"

class RawTeamStandings(TeamStandings, RawModel):
    rows: list[RawTeamStandingsEntry]
    tournament: RawTournament
    updatedAtTimestamp: Timestamp

class ParsedTeamStandings(TeamStandings, ParsedModel):
    rows: list[ParsedTeamStandingsEntry]
    tournament: ParsedTournament
    updatedAt: datetime


# =====================================================================
# Leaderboard — Racing Standings
# =====================================================================

class RacingStandingsEntry(BaseModel):
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

class RawRacingStandingsEntry(RacingStandingsEntry, RawModel):
    team: RawTeam              # Driver/Cyclist or Team/Constructor
    parentTeam: RawTeam        # Team/Constructor if team is Driver/Cyclist, else None
    updatedAtTimestamp: Timestamp

class ParsedRacingStandingsEntry(RacingStandingsEntry, ParsedModel):
    team: ParsedTeam
    parentTeam: ParsedTeam
    updatedAt: datetime


# =====================================================================
# Leaderboard — Rankings
# =====================================================================

class RankingType(BaseModel):
    id: int
    slug: str
    name: str
    gender: str
    sport: Sport
    category: Category

class RawRankingType(RankingType, RawModel):
    uniqueTournament: RawUniqueTournament
    lastUpdatedTimestamp: Timestamp

class ParsedRankingType(RankingType, ParsedModel):
    uniqueTournament: ParsedUniqueTournament
    lastUpdated: datetime


class RankingEntry(BaseModel):
    id: int
    name: str
    position: int         # For MMA, position starts at 0 instead of 1
    points: float
    country: Country
    bestPosition: int
    previousPosition: int
    previousPoints: float
    tournamentsPlayed: int

class RawRankingEntry(RankingEntry, RawModel):
    team: RawTeam
    lastEvent: RawEvent
    updatedAtTimestamp: Timestamp

class ParsedRankingEntry(RankingEntry, ParsedModel):
    team: ParsedTeam
    lastEvent: ParsedEvent
    updatedAt: datetime
