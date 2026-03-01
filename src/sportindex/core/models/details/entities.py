from __future__ import annotations

from datetime import datetime

from ..primitives import Performance, Timestamp, ISODate
from ..base import BaseModel, RawModel, ParsedModel
from ..player import RawPlayer, ParsedPlayer
from ..team import RawTeam, ParsedTeam
from ..tournament import RawUniqueTournament, ParsedUniqueTournament, RawSeason, ParsedSeason


# =====================================================================
# Team Players
# =====================================================================

class PlayerPreviousTeam(BaseModel):
    pass

class RawPlayerPreviousTeam(PlayerPreviousTeam, RawModel):
    player: RawPlayer
    previousTeam: RawTeam
    transferDate: ISODate

class ParsedPlayerPreviousTeam(PlayerPreviousTeam, ParsedModel):
    player: ParsedPlayer
    previousTeam: ParsedTeam
    transferDate: datetime


class TeamPlayers(BaseModel):
    pass

class RawTeamPlayers(TeamPlayers, RawModel):
    players: list[RawPlayer]
    foreignPlayers: list[RawPlayer]
    nationalPlayers: list[RawPlayer]
    playerPreviousTeams: list[RawPlayerPreviousTeam]

class ParsedTeamPlayers(TeamPlayers, ParsedModel):
    players: list[ParsedPlayer]
    foreignPlayers: list[ParsedPlayer]
    nationalPlayers: list[ParsedPlayer]
    playerPreviousTeams: list[ParsedPlayerPreviousTeam]


# =====================================================================
# Team Season Stats
# =====================================================================

class TeamSeasonStats(BaseModel):
    id: int
    goalsScored: int
    goalsConceded: int
    ownGoals: int
    assists: int
    shots: int
    penaltyGoals: int
    penaltiesTaken: int
    freeKickGoals: int
    freeKickShots: int
    goalsFromInsideTheBox: int
    goalsFromOutsideTheBox: int
    shotsFromInsideTheBox: int
    shotsFromOutsideTheBox: int
    headedGoals: int
    leftFootGoals: int
    rightFootGoals: int
    bigChances: int
    bigChancesCreated: int
    bigChancesMissed: int
    shotsOnTarget: int
    shotsOffTarget: int
    blockedScoringAttempt: int
    successfulDribbles: int
    dribbleAttempts: int
    corners: int
    hitWoodwork: int
    fastBreaks: int
    fastBreakGoals: int
    fastBreakShots: int
    averageBallPossession: float
    totalPasses: int
    accuratePasses: int
    accuratePassesPercentage: float
    totalOwnHalfPasses: int
    accurateOwnHalfPasses: int
    accurateOwnHalfPassesPercentage: float
    totalOppositionHalfPasses: int
    accurateOppositionHalfPasses: int
    accurateOppositionHalfPassesPercentage: float
    totalLongBalls: int
    accurateLongBalls: int
    accurateLongBallsPercentage: float
    totalCrosses: int
    accurateCrosses: int
    accurateCrossesPercentage: float
    cleanSheets: int
    tackles: int
    interceptions: int
    saves: int
    errorsLeadingToGoal: int
    errorsLeadingToShot: int
    penaltiesCommited: int
    penaltyGoalsConceded: int
    clearances: int
    clearancesOffLine: int
    lastManTackles: int
    totalDuels: int
    duelsWon: int
    duelsWonPercentage: float
    totalGroundDuels: int
    groundDuelsWon: int
    groundDuelsWonPercentage: float
    totalAerialDuels: int
    aerialDuelsWon: int
    aerialDuelsWonPercentage: float
    possessionLost: int
    offsides: int
    fouls: int
    yellowCards: int
    yellowRedCards: int
    redCards: int
    avgRating: float
    accurateFinalThirdPassesAgainst: int
    accurateOppositionHalfPassesAgainst: int
    accurateOwnHalfPassesAgainst: int
    accuratePassesAgainst: int
    bigChancesAgainst: int
    bigChancesCreatedAgainst: int
    bigChancesMissedAgainst: int
    clearancesAgainst: int
    cornersAgainst: int
    crossesSuccessfulAgainst: int
    crossesTotalAgainst: int
    dribbleAttemptsTotalAgainst: int
    dribbleAttemptsWonAgainst: int
    errorsLeadingToGoalAgainst: int
    errorsLeadingToShotAgainst: int
    hitWoodworkAgainst: int
    interceptionsAgainst: int
    keyPassesAgainst: int
    longBallsSuccessfulAgainst: int
    longBallsTotalAgainst: int
    offsidesAgainst: int
    redCardsAgainst: int
    shotsAgainst: int
    shotsBlockedAgainst: int
    shotsFromInsideTheBoxAgainst: int
    shotsFromOutsideTheBoxAgainst: int
    shotsOffTargetAgainst: int
    shotsOnTargetAgainst: int
    blockedScoringAttemptAgainst: int
    tacklesAgainst: int
    totalFinalThirdPassesAgainst: int
    oppositionHalfPassesTotalAgainst: int
    ownHalfPassesTotalAgainst: int
    totalPassesAgainst: int
    yellowCardsAgainst: int
    throwIns: int
    goalKicks: int
    ballRecovery: int
    freeKicks: int
    kilometersCovered: float
    numberOfSprints: int
    matches: int
    awardedMatches: int


# =====================================================================
# Team Year Stats (Tennis)
# =====================================================================

class TeamYearSurfaceStats(BaseModel):
    matches: int
    groundType: str        # e.g. "Hardcourt indoor", "Red clay", "Grass"
    totalServeAttempts: int
    tiebreakLosses: int
    tiebreaksWon: int
    tournamentsWon: int
    tournamentsPlayed: int
    wins: int
    aces: int
    firstServePointsScored: int
    firstServePointsTotal: int
    firstServeTotal: int
    secondServePointsScored: int
    secondServePointsTotal: int
    secondServeTotal: int
    breakPointsScored: int
    breakPointsTotal: int
    opponentBreakPointsTotal: int
    opponentBreakPointsScored: int
    winnersTotal: int
    unforcedErrorsTotal: int
    doubleFaults: int


class TeamYearStats(BaseModel):
    statistics: list[TeamYearSurfaceStats]


# =====================================================================
# Player Statistics
# =====================================================================

class PlayerSeasonStatsItem(BaseModel):
    id: int
    accurateCrosses: int
    accurateCrossesPercentage: float
    accurateLongBalls: int
    accurateLongBallsPercentage: float
    accuratePasses: int
    accuratePassesPercentage: float
    assists: int
    bigChancesCreated: int
    bigChancesMissed: int
    blockedShots: int
    cleanSheet: int
    dribbledPast: int
    errorLeadToGoal: int
    expectedAssists: float
    expectedGoals: float
    goals: int
    goalsAssistsSum: int
    goalsConceded: int
    interceptions: int
    keyPasses: int
    minutesPlayed: int
    passToAssist: int
    rating: float
    redCards: int
    saves: int
    shotsOnTarget: int
    successfulDribbles: int
    tackles: int
    totalShots: int
    yellowCards: int
    totalRating: float
    countRating: int
    totalLongBalls: int
    totalCross: int
    totalPasses: int
    shotsFromInsideTheBox: int
    appearances: int


class PlayerSeasonStats(BaseModel):
    year: str
    startYear: int
    endYear: int
    statistics: PlayerSeasonStatsItem

class RawPlayerSeasonStats(PlayerSeasonStats, RawModel):
    team: RawTeam
    uniqueTournament: RawUniqueTournament
    season: RawSeason

class ParsedPlayerSeasonStats(PlayerSeasonStats, ParsedModel):
    team: ParsedTeam
    uniqueTournament: ParsedUniqueTournament
    season: ParsedSeason


# =====================================================================
# Manager Career History
# =====================================================================

class ManagerCareerHistoryItem(BaseModel):
    performance: Performance

class RawManagerCareerHistoryItem(ManagerCareerHistoryItem, RawModel):
    team: RawTeam
    startTimestamp: Timestamp
    endTimestamp: Timestamp

class ParsedManagerCareerHistoryItem(ManagerCareerHistoryItem, ParsedModel):
    team: ParsedTeam
    startTimestamp: datetime
    endTimestamp: datetime


# =====================================================================
# Venue Statistics
# =====================================================================

class VenueStatistics(BaseModel):
    totalMatches: int
    homeTeamGoalsScored: int
    awayTeamGoalsScored: int
    avgRedCardsPerGame: float
    avgCornerKicksPerGame: float
    homeTeamWinsPercentage: float
    awayTeamWinsPercentage: float
    drawsPercentage: float
