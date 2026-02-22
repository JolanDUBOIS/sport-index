"""
Event-related TypedDict types: events, lineups, statistics, incidents,
momentum graph, and all Parsed* output types from parsers.py.

See __init__.py for full package docstring and conventions.
"""

from __future__ import annotations

from typing import TypedDict

from .common import RawStatus
from .entities import (
    RawManager,
    RawPlayer,
    RawReferee,
    RawSeason,
    RawTeam,
    RawTournament,
    RawVenue,
)


# =====================================================================
# Event
# =====================================================================

class RawRound(TypedDict, total=False):
    """Round info, nested under ``roundInfo`` in event responses."""
    number: int
    name: str
    slug: str


class RawEventScore(TypedDict, total=False):
    """Score dict within an event (the ``homeScore`` / ``awayScore`` objects).

    Contains a ``display`` key for the final/current score, plus per-period
    keys like ``period1``, ``period2``, ``overtime``, ``penalties``, and tiebreak
    keys like ``period1TieBreak``.

    REMARK: The set of keys is dynamic and depends on sport configuration.
    Only the most common keys are typed here.
    """
    display: int
    current: int
    period1: int
    period2: int
    period3: int
    period4: int
    period5: int
    overtime: int
    penalties: int
    normaltime: int           # ASSUMPTION: seen in some football events
    period1TieBreak: int
    period2TieBreak: int
    period3TieBreak: int
    period4TieBreak: int
    period5TieBreak: int


class RawEventTime(TypedDict, total=False):
    """The ``time`` dict within an event, containing period durations
    and injury time values."""
    period1: int
    period2: int
    injuryTime1: int
    injuryTime2: int
    injuryTime3: int
    injuryTime4: int
    # REMARK: More injuryTime keys may exist for overtime periods


class RawEventPeriodLabels(TypedDict, total=False):
    """The ``periods`` dict within an event, mapping period keys to labels.
    E.g. {"period1": "1st Set", "period2": "2nd Set", "overtime": "Overtime"}
    ASSUMPTION: Keys match the period keys in RawEventScore.
    """
    period1: str
    period2: str
    period3: str
    period4: str
    period5: str
    overtime: str
    penalties: str
    period1TieBreak: str  # ASSUMPTION: not sure if labels exist for tiebreaks


class RawEvent(TypedDict, total=False):
    id: int
    customId: str
    slug: str
    startTimestamp: int              # Unix timestamp
    season: RawSeason
    tournament: RawTournament
    homeTeam: RawTeam
    awayTeam: RawTeam
    status: RawStatus
    roundInfo: RawRound
    # Period / score info
    defaultPeriodCount: int
    defaultPeriodLength: int         # In minutes — ASSUMPTION
    defaultOvertimeLength: int
    homeScore: RawEventScore
    awayScore: RawEventScore
    time: RawEventTime
    periods: RawEventPeriodLabels    # Period key → label name mapping
    # General
    gender: str
    referee: RawReferee
    venue: RawVenue
    attendance: int
    winnerCode: int                  # 1=home, 2=away, 3=draw
    # Racket sports
    firstToServe: int                # ASSUMPTION: 1 or 2 for home/away?
    # Fight sports (MMA, boxing)
    fightType: str
    order: list[int]                 # ASSUMPTION: fight card position?
    weightClass: str
    winType: str
    finalRound: int


class RawEventsResponse(TypedDict, total=False):
    """Wrapper for paginated event list endpoints."""
    events: list[RawEvent]
    hasNextPage: bool


# =====================================================================
# Lineups
# =====================================================================

class RawLineup(TypedDict, total=False):
    players: list[RawPlayer]
    missingPlayers: list[RawPlayer]
    formation: str                  # e.g. "4-3-3"


class RawLineupsResponse(TypedDict, total=False):
    """Response from /event/{id}/lineups.
    REMARK: The actual response nests this under a ``lineups`` key which
    the provider already extracts for you.
    """
    home: RawLineup
    away: RawLineup


# =====================================================================
# Event Statistics
# =====================================================================

class RawStatisticsItem(TypedDict, total=False):
    key: str                      # e.g. "ballPossession", "totalShots"
    name: str                     # Display name, e.g. "Ball possession"
    home: str                     # String representation, e.g. "54%"
    away: str
    compareCode: int              # 1=home better, 2=away better, 3=tied
    statisticsType: str           # "positive" or "negative"
    # REMARK: API also returns `valueType`, `homeValue`, `awayValue`,
    # `renderType` — not typed here, but accessible on the dict.
    homeValue: int | float
    awayValue: int | float
    valueType: str
    renderType: int


class RawStatisticsGroup(TypedDict, total=False):
    groupName: str                    # e.g. "Match overview", "Shots"
    statisticsItems: list[RawStatisticsItem]


class RawPeriodStatistics(TypedDict, total=False):
    period: str                       # e.g. "ALL", "1ST", "2ND"
    groups: list[RawStatisticsGroup]


class RawEventStatisticsResponse(TypedDict, total=False):
    """Response from /event/{id}/statistics."""
    statistics: list[RawPeriodStatistics]


# =====================================================================
# Momentum Graph
# =====================================================================

class RawMomentumPoint(TypedDict, total=False):
    minute: float
    value: int  # positive=home, negative=away, range ~[-100, 100]


class RawMomentumGraphResponse(TypedDict, total=False):
    """Response from /event/{id}/graph."""
    graphPoints: list[RawMomentumPoint]
    periodTime: int
    periodCount: int
    overtimeLength: int


# =====================================================================
# Incidents
# =====================================================================

class RawIncident(TypedDict, total=False):
    """Superset of all fields across all incident types.

    The ``incidentType`` key tells you which subset of fields is populated:
      - "goal"            → player (scorer), assist, incidentClass ("regular", "ownGoal", "penalty")
      - "penalty"         → player (shooter), incidentClass ("missed", etc.)
      - "penaltyShootout" → player (shooter), incidentClass ("scored", "missed")
      - "card"            → player OR manager, incidentClass ("yellow", "red"), rescinded, reason
      - "period"          → text (e.g. "HT", "FT"), time may be 999 (= no meaningful time)
      - "varDecision"     → incidentClass ("goalAwarded", "penaltyCheck"...), confirmed, text
      - "substitution"    → playerIn, playerOut, incidentClass ("regular", "injury")
      - "injuryTime"      → length (the added time in minutes)

    REMARK: More incident types may exist in other sports. The current codebase
    warns and skips unknowns. Consider adding them as you discover them.
    """
    incidentType: str
    id: int
    time: int
    addedTime: int                      # Extra time / stoppage time minute offset
    isHome: bool                        # True=home side, False=away side
    homeScore: int                      # Running score at the time of incident
    awayScore: int
    incidentClass: str                  # Subtype within the incident (e.g. "regular", "yellow")
    # Goal / Penalty / Card / Shootout
    player: RawPlayer                   # The primary player (scorer, shooter, card recipient)
    assist: RawPlayer                   # Goal assist
    # Card
    manager: RawManager                 # Card can be given to a manager
    rescinded: bool
    reason: str
    # Period / VAR
    text: str                           # Period label ("HT"), VAR description
    confirmed: bool                     # VAR decision confirmed or not
    # Substitution
    playerIn: RawPlayer
    playerOut: RawPlayer
    # Injury time incident
    length: int                         # Minutes of added time
    # Penalty
    description: str
    # Fight sports — ASSUMPTION: there may be fight-specific incident fields


# =====================================================================
# Parsed Output Types (from parsers.py)
# These are NOT raw API shapes — they are computed by parse functions.
# =====================================================================

class ParsedScore(TypedDict, total=False):
    """Simple home/away score pair, used in parsed periods and incidents."""
    home: int | None
    away: int | None


class ParsedPeriod(TypedDict, total=False):
    """A single period as reconstructed by parse_periods().
    The key/type pair uniquely identifies the period.
    """
    key: str               # e.g. "period1", "overtime", "penalties", "period2TieBreak"
    type: str              # "normal", "overtime", "tiebreak", "penalties"
    label: str | None      # Display label, e.g. "1st Half", "Overtime"
    score: ParsedScore | None
    time: int | None       # Actual elapsed time for this period (if known)
    defaultTime: int | None
    extraTime: list[int] | None  # Injury/stoppage time added in this period


class ParsedPeriods(TypedDict):
    """Output of parse_periods(). Reconstructs period structure from the
    scattered score/time keys in a raw event dict."""
    defaultCount: int
    periods: list[ParsedPeriod]


# -- Parsed Incidents --------------------------------------------------
# Each incident type gets its own TypedDict so the higher layer
# (and your IDE) can see exactly what fields are available.
# All of them carry `incidentType` so you can still dispatch on it.

class ParsedGoalIncident(TypedDict, total=False):
    incidentType: str          # always "goal"
    id: int
    time: int
    side: str | None           # "home" / "away"
    score: ParsedScore | None  # running score at time of goal
    scorer: dict               # raw player dict — kept as-is for the higher layer
    assist: dict | None        # raw player dict
    extraTime: int | None      # stoppage-time minute offset
    kind: str | None           # "regular", "ownGoal", "penalty" (football); "try", "twoPoints"... (rugby)


class ParsedPenaltyIncident(TypedDict, total=False):
    """A missed in-play penalty (scored penalties come as GoalIncident)."""
    incidentType: str          # always "penalty"
    id: int
    time: int
    side: str | None
    shooter: dict              # raw player dict
    extraTime: int | None
    description: str | None
    kind: str | None           # "missed", etc.


class ParsedPenaltyShootoutIncident(TypedDict, total=False):
    incidentType: str          # always "penaltyShootout"
    id: int
    side: str | None
    score: ParsedScore | None  # running shootout score
    shooter: dict              # raw player dict
    kind: str | None           # "scored", "missed"


class ParsedCardIncident(TypedDict, total=False):
    incidentType: str          # always "card"
    id: int
    time: int                  # -5 means card given on bench
    side: str | None
    recipient: dict            # raw player OR manager dict
    recipientType: str         # "player" or "manager" — tells you which dict shape it is
    rescinded: bool
    reason: str | None
    extraTime: int | None
    kind: str | None           # "yellow", "red", "yellowRed"


class ParsedPeriodIncident(TypedDict, total=False):
    incidentType: str          # always "period"
    time: int | None           # API sends 999 for "no time" → normalised to None
    score: ParsedScore | None
    kind: str | None           # "HT", "FT", "PEN", etc.


class ParsedVarDecisionIncident(TypedDict, total=False):
    incidentType: str          # always "varDecision"
    id: int
    time: int
    side: str | None
    extraTime: int | None
    description: str | None
    kind: str | None           # "goalAwarded", "penaltyCheck", etc.
    confirmed: bool | None


class ParsedSubstitutionIncident(TypedDict, total=False):
    incidentType: str          # always "substitution"
    id: int
    time: int
    side: str | None
    playerIn: dict             # raw player dict
    playerOut: dict            # raw player dict
    extraTime: int | None
    kind: str | None           # "regular", "injury"


class ParsedExtraTimeIncident(TypedDict, total=False):
    """Injury/added time announcement (not a substitution or event)."""
    incidentType: str          # always "injuryTime"
    time: int
    addedTime: int             # minutes of added time


# Union of all parsed incident types — for type annotations
ParsedIncident = (
    ParsedGoalIncident
    | ParsedPenaltyIncident
    | ParsedPenaltyShootoutIncident
    | ParsedCardIncident
    | ParsedPeriodIncident
    | ParsedVarDecisionIncident
    | ParsedSubstitutionIncident
    | ParsedExtraTimeIncident
)
