from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, TypedDict

from ..base import BaseParsedModel
from ..parsers import parse_timestamp, parse_iso
if TYPE_CHECKING:
    from ..team import ParsedTeam
    from ..player import ParsedPlayer
    from ..tournament import ParsedUniqueTournament, ParsedSeason
    from sportindex.core.provider.raw.models import (
        PlayerPreviousTeam, TeamPlayers,
        PlayerSeasonStats, ManagerCareerHistoryItem,
        PlayerSeasonStatsItem, Performance, 
        TeamSeasonStats, TeamYearSurfaceStats, TeamYearStats
    )


# =====================================================================
# Team Players
# =====================================================================

@dataclass
class ParsedPlayerPreviousTeam(BaseParsedModel):
    player: ParsedPlayer
    previousTeam: ParsedTeam
    transferDate: datetime

    @classmethod
    def _parse(cls, raw: PlayerPreviousTeam) -> ParsedPlayerPreviousTeam:
        from ..player import ParsedPlayer
        from ..team import ParsedTeam
        return cls(
            player=ParsedPlayer.from_raw(raw.get("player")),
            previousTeam=ParsedTeam.from_raw(raw.get("previousTeam")),
            transferDate=parse_iso(raw.get("transferDate"))
        )


@dataclass
class ParsedTeamPlayers(BaseParsedModel):
    players: list[ParsedPlayer]
    foreignPlayers: list[ParsedPlayer]
    nationalPlayers: list[ParsedPlayer]
    playerPreviousTeams: list[ParsedPlayerPreviousTeam]

    @classmethod
    def _parse(cls, raw: TeamPlayers) -> ParsedTeamPlayers:
        from ..player import ParsedPlayer
        return cls(
            players=[ParsedPlayer.from_raw(p) for p in raw.get("players", [])],
            foreignPlayers=[ParsedPlayer.from_raw(p) for p in raw.get("foreignPlayers", [])],
            nationalPlayers=[ParsedPlayer.from_raw(p) for p in raw.get("nationalPlayers", [])],
            playerPreviousTeams=[ParsedPlayerPreviousTeam.from_raw(t) for t in raw.get("playerPreviousTeams", [])]
        )


# =====================================================================
# Team Season Stats
# =====================================================================

@dataclass
class ParsedTeamSeasonStats(BaseParsedModel):
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

    @classmethod
    def _parse(cls, raw: TeamSeasonStats) -> ParsedTeamSeasonStats:
        return cls(**raw.values())


# =====================================================================
# Team Year Stats (Tennis)
# =====================================================================

@dataclass
class ParsedTeamYearStats(BaseParsedModel):
    statistics: list[TeamYearSurfaceStats]

    @classmethod
    def _parse(cls, raw: TeamYearStats) -> ParsedTeamYearStats:
        return cls(statistics=raw.get("statistics", []))


# =====================================================================
# Player Statistics
# =====================================================================

@dataclass
class ParsedPlayerSeasonStats(BaseParsedModel):
    year: str
    startYear: int
    endYear: int
    statistics: PlayerSeasonStatsItem
    team: ParsedTeam
    uniqueTournament: ParsedUniqueTournament
    season: ParsedSeason

    @classmethod
    def _parse(cls, raw: PlayerSeasonStats) -> ParsedPlayerSeasonStats:
        from ..team import ParsedTeam
        from ..tournament import ParsedUniqueTournament, ParsedSeason
        return cls(
            year=raw.get("year"),
            startYear=raw.get("startYear"),
            endYear=raw.get("endYear"),
            statistics=raw.get("statistics"),
            team=ParsedTeam.from_raw(raw.get("team")),
            uniqueTournament=ParsedUniqueTournament.from_raw(raw.get("uniqueTournament")),
            season=ParsedSeason.from_raw(raw.get("season"))
        )


# =====================================================================
# Manager Career History
# =====================================================================

@dataclass
class ParsedManagerCareerHistoryItem(BaseParsedModel):
    performance: Performance
    team: ParsedTeam
    startTimestamp: datetime
    endTimestamp: datetime

    @classmethod
    def _parse(cls, raw: ManagerCareerHistoryItem) -> ParsedManagerCareerHistoryItem:
        from ..team import ParsedTeam
        return cls(
            performance=raw.get("performance"),
            team=ParsedTeam.from_raw(raw.get("team")),
            startTimestamp=parse_timestamp(raw.get("startTimestamp")),
            endTimestamp=parse_timestamp(raw.get("endTimestamp"))
        )