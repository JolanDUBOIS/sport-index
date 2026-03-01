from __future__ import annotations

from datetime import datetime

from .base import BaseModel, RawModel, ParsedModel
from .primitives import Timestamp, Status
from .referee import RawReferee, ParsedReferee
from .team import RawTeam, ParsedTeam
from .tournament import RawTournament, ParsedTournament, RawSeason, ParsedSeason
from .venue import RawVenue, ParsedVenue


# =====================================================================
# Event
# =====================================================================

class Event(BaseModel):
    id: int
    customId: str
    slug: str
    gender: str
    roundInfo: Round
    previousLegEventId: int

    # Teams / participants
    homeTeamSeed: int
    awayTeamSeed: int
    homeTeamRanking: int
    awayTeamRanking: int
    attendance: int

    # Status & result
    status: Status
    winnerCode: int                   # 1=home, 2=away, 3=draw

    # Period / scoring info (when event is in-play or finished)
    defaultPeriodCount: int
    defaultPeriodLength: int
    defaultOvertimeLength: int
    homeScore: EventScore
    awayScore: EventScore
    time: EventTime
    periods: EventPeriodLabels      # Period key → label mapping

    # Racket sports specific
    firstToServe: int

    # Fight sports (MMA, boxing)
    fightType: str                     # e.g. "maincard"
    weightClass: str
    winType: str
    finalRound: int
    order: list[int]

class RawEvent(Event, RawModel):
    startTimestamp: Timestamp
    season: RawSeason
    tournament: RawTournament

    # Teams / participants
    homeTeam: RawTeam
    awayTeam: RawTeam
    referee: RawReferee
    venue: RawVenue

class ParsedEvent(Event, ParsedModel):
    startTimestamp: datetime
    season: ParsedSeason
    tournament: ParsedTournament

    # Teams / participants
    homeTeam: ParsedTeam
    awayTeam: ParsedTeam
    referee: ParsedReferee
    venue: ParsedVenue


# =====================================================================
# Primitives
# =====================================================================

class Round(BaseModel):
    name: str
    slug: str
    round: int


class EventScore(BaseModel):
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


class EventTime(BaseModel):
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


class EventPeriodLabels(BaseModel):
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
