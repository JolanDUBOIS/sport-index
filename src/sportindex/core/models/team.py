from __future__ import annotations

from datetime import datetime

from .base import BaseModel, RawModel, ParsedModel
from .common import Category, Sport, Country
from .manager import RawManager, ParsedManager
from .primitives import Timestamp, Amount
from .tournament import RawTournament, ParsedTournament, RawUniqueTournament, ParsedUniqueTournament
from .venue import RawVenue, ParsedVenue

# =====================================================================
# Team
# =====================================================================

class Team(BaseModel):
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

class RawTeam(Team, RawModel):
    tournament: RawTournament
    primaryUniqueTournament: RawUniqueTournament
    manager: RawManager
    venue: RawVenue
    foundationDateTimestamp: Timestamp
    parentTeam: RawTeam
    playerTeamInfo: RawPlayerTeamInfo

class ParsedTeam(Team, ParsedModel):
    tournament: ParsedTournament
    primaryUniqueTournament: ParsedUniqueTournament
    manager: ParsedManager
    venue: ParsedVenue
    foundationDateTimestamp: datetime
    parentTeam: ParsedTeam
    playerTeamInfo: ParsedPlayerTeamInfo


# =====================================================================
# Player Info (for individual athletes represented as teams)
# =====================================================================

class PlayerTeamInfo(BaseModel):
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

class RawPlayerTeamInfo(PlayerTeamInfo, RawModel):
    birthDateTimestamp: Timestamp

class ParsedPlayerTeamInfo(PlayerTeamInfo, ParsedModel):
    birthDateTimestamp: datetime
