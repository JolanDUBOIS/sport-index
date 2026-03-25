from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from .core import RawCategory, RawSport, RawCountry
    from .manager import RawManager
    from .primitives import Timestamp, RawAmount
    from .tournament import RawTournament, RawUniqueTournament
    from .venue import RawVenue


# =====================================================================
# Player Info (for individual athletes represented as teams)
# =====================================================================

class RawPlayerTeamInfo(TypedDict, total=False):
    id: int
    residence: str
    birthplace: str
    height: float        # in m (e.g. 1.85)
    weight: float        # in kg
    number: int
    plays: str           # e.g. "right-handed"
    mainDriver: bool
    turnedPro: str       # e.g. "2018"
    prizeCurrentRaw: RawAmount
    prizeTotalRaw: RawAmount
    currentRanking: int
    birthDateTimestamp: Timestamp


# =====================================================================
# Team
# =====================================================================

class RawTeam(TypedDict, total=False):
    id: int
    slug: str
    name: str
    shortName: str
    fullName: str
    nameCode: str        # e.g. "PSG", "BAR"
    gender: str          # "M", "F"
    sport: RawSport
    category: RawCategory
    country: RawCountry
    national: bool
    disabled: bool
    ranking: int
    tournament: RawTournament
    primaryUniqueTournament: RawUniqueTournament
    manager: RawManager
    venue: RawVenue
    foundationDateTimestamp: Timestamp
    parentTeam: RawTeam
    playerTeamInfo: RawPlayerTeamInfo
