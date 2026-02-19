from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from .common import Amount
from .core import BaseModel, Country, Sport, Category
from .utils import timestamp_to_iso
if TYPE_CHECKING:
    from .manager import Manager
    from .tournament import UniqueTournament
    from .venue import Venue


@dataclass(frozen=True, kw_only=True)
class PlayerTeamInfo(BaseModel): # When a team is a player for an individual sport (e.g. tennis)
    id: str
    residence: Optional[str] = None
    birth_place: Optional[str] = None
    height: Optional[float] = None # in m
    weight: Optional[float] = None # in kg
    handedness: Optional[str] = None # e.g. "right-handed", "left-handed"...
    prize_current: Optional[Amount] = None
    prize_total: Optional[Amount] = None
    date_of_birth: Optional[str] = None
    current_ranking: Optional[int] = None

    @classmethod
    def _from_api(cls, raw: dict) -> PlayerTeamInfo:
        return PlayerTeamInfo(
            id=raw.get("id"),
            residence=raw.get("residence"),
            birth_place=raw.get("birthplace"),
            height=raw.get("height"),
            weight=raw.get("weight"),
            handedness=raw.get("handedness"),
            prize_current=Amount.from_api(raw.get("prizeCurrentRaw")),
            prize_total=Amount.from_api(raw.get("prizeTotalRaw")),
            date_of_birth=timestamp_to_iso(raw.get("birthDateTimestamp"), kind="date"),
            current_ranking=raw.get("currentRanking"),
        )


@dataclass(frozen=True, kw_only=True)
class Team(BaseModel):
    id: str
    slug: str
    name: str
    short_name: str
    full_name: str
    name_code: str
    national: bool
    disabled: bool
    gender: str
    country: Country
    category: Category
    sport: Sport
    primary_unique_tournament: Optional[UniqueTournament] = None
    manager: Optional[Manager] = None
    parent: Optional[Team] = None
    venue: Optional[Venue] = None
    ranking: Optional[int] = None
    founded: Optional[str] = None
    player_team_info: Optional[PlayerTeamInfo] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Team:
        from .manager import Manager # Avoid circular imports
        from .tournament import UniqueTournament # Avoid circular imports
        from .venue import Venue # Avoid circular imports
        return Team(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            short_name=raw.get("shortName"),
            full_name=raw.get("fullName"),
            name_code=raw.get("nameCode"),
            national=raw.get("national"),
            disabled=raw.get("disabled"),
            gender=raw.get("gender"),
            country=Country.from_api(raw.get("country")),
            category=Category.from_api(raw.get("category")),
            sport=Sport.from_api(raw.get("sport")),
            primary_unique_tournament=UniqueTournament.from_api(raw.get("primaryUniqueTournament")),
            manager=Manager.from_api(raw.get("manager")),
            parent=Team.from_api(raw.get("parentTeam")),
            venue=Venue.from_api(raw.get("venue")),
            ranking=raw.get("ranking"),
            founded=timestamp_to_iso(raw.get("foundationDateTimestamp"), kind="date"),
            player_team_info=PlayerTeamInfo.from_api(raw.get("playerTeamInfo", {})),
        )

# Note - Additional keys:
# - wdlRecords (MMA)
