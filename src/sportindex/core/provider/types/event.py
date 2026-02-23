"""
Event-related TypedDict types: events, lineups, statistics, incidents,
momentum graph, and all Parsed* output types from parsers.py.

See __init__.py for full package docstring and conventions.
"""

from __future__ import annotations

from typing import TypedDict

from .entities import (
    RawReferee,
    RawTeam,
    RawVenue,
)
from .tournament import RawSeason, RawTournament
from .primitives import RawStatus


# =====================================================================
# Event
# =====================================================================

class RawRound(TypedDict, total=False):
    """Round info, nested under ``roundInfo`` in event responses."""
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

    # When fixed-length periods (e.g. basketball)
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


class RawEvent(TypedDict, total=False):
    id: int
    customId: str
    slug: str
    startTimestamp: int
    gender: str
    season: RawSeason
    tournament: RawTournament
    roundInfo: RawRound
    previousLegEventId: int

    # Teams / participants
    homeTeam: RawTeam
    awayTeam: RawTeam
    homeTeamSeed: int
    awayTeamSeed: int
    homeTeamRanking: int
    awayTeamRanking: int
    referee: RawReferee
    venue: RawVenue
    attendance: int

    # Status & result
    status: RawStatus
    winnerCode: int                   # 1=home, 2=away, 3=draw

    # Period / scoring info (when event is in-play or finished)
    defaultPeriodCount: int
    defaultPeriodLength: int
    defaultOvertimeLength: int
    homeScore: RawEventScore
    awayScore: RawEventScore
    time: RawEventTime
    periods: RawEventPeriodLabels      # Period key → label mapping

    # Racket sports specific
    firstToServe: int

    # Fight sports (MMA, boxing)
    fightType: str                     # e.g. "maincard"
    weightClass: str
    winType: str
    finalRound: int
    order: list[int]


class RawEventsResponse(TypedDict, total=False):
    """Wrapper for paginated event list endpoints."""
    events: list[RawEvent]
    hasNextPage: bool
