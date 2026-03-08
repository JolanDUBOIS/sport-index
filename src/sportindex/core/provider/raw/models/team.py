from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from .main import Category, Sport, Country
    from .manager import Manager
    from .primitives import Timestamp, Amount
    from .tournament import Tournament, UniqueTournament
    from .venue import Venue


# =====================================================================
# Player Info (for individual athletes represented as teams)
# =====================================================================

class PlayerTeamInfo(TypedDict, total=False):
    id: int
    residence: str
    birthplace: str
    height: float        # in m (e.g. 1.85)
    weight: float        # in kg
    number: int
    plays: str           # e.g. "right-handed"
    mainDriver: bool
    turnedPro: str       # e.g. "2018"
    prizeCurrentRaw: Amount
    prizeTotalRaw: Amount
    currentRanking: int
    birthDateTimestamp: Timestamp


# =====================================================================
# Team
# =====================================================================

class Team(TypedDict, total=False):
    id: int
    slug: str
    name: str
    shortName: str
    fullName: str
    nameCode: str        # e.g. "PSG", "BAR"
    gender: str          # "M", "F"
    sport: Sport
    category: Category
    country: Country
    national: bool
    disabled: bool
    ranking: int
    tournament: Tournament
    primaryUniqueTournament: UniqueTournament
    manager: Manager
    venue: Venue
    foundationDateTimestamp: Timestamp
    parentTeam: Team
    playerTeamInfo: PlayerTeamInfo
