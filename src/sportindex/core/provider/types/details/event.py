from typing import TypedDict

from ..entities import RawPlayer, RawManager


# =====================================================================
# Lineups
# =====================================================================

class RawLineup(TypedDict, total=False):
    players: list[RawPlayer]
    missingPlayers: list[RawPlayer]
    formation: str                  # e.g. "4-3-3"


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


# =====================================================================
# Momentum Graph
# =====================================================================

class RawMomentumPoint(TypedDict, total=False):
    minute: float
    value: int  # positive=home, negative=away, range ~[-100, 100]


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
