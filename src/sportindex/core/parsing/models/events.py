from __future__ import annotations

from typing import Optional

from .common import ParsedScore
from sportindex.core.base import BaseModel
from sportindex.core.provider.models import (
    RawRound, RawSeason,
    RawTournament, RawReferee, RawTeam,
    RawVenue, RawStatus, Timestamp
)


class ParsedEvent(BaseModel):
    id: int
    customId: str
    slug: str
    startTimestamp: Timestamp
    gender: str
    season: RawSeason
    tournament: RawTournament
    roundInfo: RawRound
    previousLegEventId: int

    referee: RawReferee
    venue: RawVenue
    attendance: int

    status: RawStatus
    winnerCode: int

    # Grouped fields
    home: ParsedTeam
    away: ParsedTeam
    extra: Optional[ParsedExtra]

    # Parsed periods
    parsedPeriods: ParsedPeriods

class ParsedTeam(BaseModel):
    team: RawTeam
    seed: int
    ranking: int
    score: int

class ParsedFightExtra(BaseModel):
    fightType: str
    weightClass: str
    winType: str
    finalRound: int
    order: list[int]

class ParsedRacketExtra(BaseModel):
    firstToServe: int

ParsedExtra = ParsedFightExtra | ParsedRacketExtra


class ParsedPeriod(BaseModel):
    """A single period as reconstructed by parse_periods().
    The key/type pair uniquely identifies the period.
    """
    key: str                                # e.g. "period1", "overtime", "penalties", "period2TieBreak"
    type: str                               # "normal", "overtime", "tiebreak", "penalties"
    label: Optional[str] = None             # Display label, e.g. "1st Half", "Overtime"
    score: Optional[ParsedScore] = None
    time: Optional[int] = None              # Actual elapsed time for this period (if known)
    defaultTime: Optional[int] = None
    extraTime: Optional[list[int]] = None   # Injury/stoppage time added in this period

class ParsedPeriods(BaseModel):
    """Output of parse_periods(). Reconstructs period structure from the
    scattered score/time keys in a raw event dict."""
    defaultCount: int
    periods: list[ParsedPeriod]
