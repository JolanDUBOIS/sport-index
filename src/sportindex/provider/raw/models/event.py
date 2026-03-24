from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from .primitives import Timestamp, RawStatus
    from .referee import RawReferee
    from .team import RawTeam
    from .tournament import RawTournament, RawSeason
    from .venue import RawVenue


# =====================================================================
# Primitives
# =====================================================================

class RawRound(TypedDict, total=False):
    name: str
    slug: str
    round: int


class RawEventScore(TypedDict, total=False):
    display: int
    current: int
    period1: int
    period2: int
    period3: int
    period4: int
    period5: int
    period6: int
    period7: int
    period8: int
    period9: int
    overtime: int
    penalties: int
    normaltime: int
    aggregated: int
    period1TieBreak: int
    period2TieBreak: int
    period3TieBreak: int
    period4TieBreak: int
    period5TieBreak: int


class RawEventTime(TypedDict, total=False):
    played: int
    period1: int
    period2: int
    period3: int
    period4: int
    period5: int
    period6: int
    period7: int
    period8: int
    period9: int
    injuryTime1: int
    injuryTime2: int
    injuryTime3: int
    injuryTime4: int

    # When qxed-length periods (e.g. basketball)
    periodLength: int
    overtimeLength: int
    totalPeriodCount: int


class RawEventPeriodLabels(TypedDict, total=False):
    period1: str
    period2: str
    period3: str
    period4: str
    period5: str
    period6: str
    period7: str
    period8: str
    period9: str
    overtime: str


# =====================================================================
# Event
# =====================================================================

class RawEvent(TypedDict, total=False):
    # From base Event
    id: int
    customId: str
    slug: str
    gender: str
    startTimestamp: Timestamp
    roundInfo: RawRound

    season: RawSeason
    tournament: RawTournament
    
    attendance: int
    status: RawStatus
    previousLegEventId: int

    # Teams / participants
    homeTeam: RawTeam
    homeTeamSeed: int
    homeTeamRanking: int
    awayTeam: RawTeam
    awayTeamSeed: int
    awayTeamRanking: int
    referee: RawReferee
    venue: RawVenue

    # Period / scoring info (when event is in-play or finished)
    defaultPeriodCount: int
    defaultPeriodLength: int
    defaultOvertimeLength: int
    homeScore: RawEventScore
    awayScore: RawEventScore
    time: RawEventTime
    periods: RawEventPeriodLabels      # Period key → label mapping
    winnerCode: int                   # 1=home, 2=away, 3=draw

    # Racket sports specific
    firstToServe: int

    # Fight sports (MMA, boxing)
    fightType: str                     # e.g. "maincard"
    weightClass: str
    winType: str
    finalRound: int
    order: list[int]
