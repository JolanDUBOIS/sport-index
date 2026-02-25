from __future__ import annotations

from typing import TYPE_CHECKING

from ..base import RawModel

if TYPE_CHECKING:
    from ..entities import RawPlayer, RawTeam
    from ..primitives import RawPerformance, Timestamp, ISODate
    from ..tournament import RawUniqueTournament, RawSeason


# =====================================================================
# Team Players
# =====================================================================

class RawPlayerPreviousTeam(RawModel):
    player: RawPlayer
    previousTeam: RawTeam
    transferDate: ISODate


class RawTeamPlayers(RawModel):
    players: list[RawPlayer]
    foreignPlayers: list[RawPlayer]
    nationalPlayers: list[RawPlayer]
    playerPreviousTeams: list[RawPlayerPreviousTeam]


# =====================================================================
# Team Season Stats
# =====================================================================

class RawTeamSeasonStats(RawModel):
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

class RawTeamYearSurfaceStats(RawModel):
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


class RawTeamYearStats(RawModel):
    statistics: list[RawTeamYearSurfaceStats]


# =====================================================================
# Player Statistics
# =====================================================================

class RawPlayerSeasonStatsItem(RawModel):
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

class RawPlayerSeasonStats(RawModel):
    team: RawTeam
    year: str
    startYear: int
    endYear: int
    uniqueTournament: RawUniqueTournament
    season: RawSeason
    statistics: RawPlayerSeasonStatsItem


# =====================================================================
# Manager Career History
# =====================================================================

class RawManagerCareerHistoryItem(RawModel):
    team: RawTeam
    performance: RawPerformance
    startTimestamp: Timestamp
    endTimestamp: Timestamp


# =====================================================================
# Venue Statistics
# =====================================================================

class RawVenueStatistics(RawModel):
    totalMatches: int
    homeTeamGoalsScored: int
    awayTeamGoalsScored: int
    avgRedCardsPerGame: float
    avgCornerKicksPerGame: float
    homeTeamWinsPercentage: float
    awayTeamWinsPercentage: float
    drawsPercentage: float
