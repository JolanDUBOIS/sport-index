from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .common import Amount
from .core import BaseModel, Country
from .team import Team
from .utils import timestamp_to_iso, iso_to_iso


@dataclass(frozen=True, kw_only=True)
class Position(BaseModel):
    position: str
    primary: Optional[str] = None
    detailed: Optional[list[str]] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Position:
        return Position(
            position=raw.get("position"),
            primary=raw.get("primaryPosition"),
            detailed=raw.get("positionsDetailed"),
        )

@dataclass(frozen=True, kw_only=True)
class Player(BaseModel):
    id: str
    slug: str
    name: str
    short_name: str
    gender: str
    number: int
    team: Team
    position: Position
    country: Country
    weight: Optional[int] = None
    height: Optional[int] = None
    date_of_birth: Optional[str] = None
    status: Optional[str] = None
    retired: Optional[bool] = None
    deceased: Optional[bool] = None
    proposed_market_value: Optional[Amount] = None
    salary: Optional[Amount] = None
    preferred_foot: Optional[str] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Player:
        return Player(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            short_name=raw.get("shortName"),
            gender=raw.get("gender"),
            number=raw.get("shirtNumber"),
            team=Team.from_api(raw.get("team")),
            position=Position.from_api(raw),
            country=Country.from_api(raw.get("country")),
            weight=raw.get("weight"),
            height=raw.get("height"),
            date_of_birth=timestamp_to_iso(raw.get("dateOfBirthTimestamp"), kind="date"),
            status=raw.get("status"),
            retired=raw.get("retired"),
            deceased=raw.get("deceased"),
            proposed_market_value=Amount.from_api(raw.get("proposedMarketValueRaw")),
            salary=Amount.from_api(raw.get("salaryRaw")),
            preferred_foot=raw.get("preferredFoot"),
        )

@dataclass(frozen=True, kw_only=True)
class PlayerPreviousTeam(BaseModel):
    player: Player
    team: Team
    transfer_date: str

    @classmethod
    def _from_api(cls, raw: dict) -> PlayerPreviousTeam:
        return PlayerPreviousTeam(
            player=Player.from_api(raw.get("player", {})),
            team=Team.from_api(raw.get("previousTeam", {})),
            transfer_date=iso_to_iso(raw.get("transferDate"), kind="date")
        )

@dataclass(frozen=True, kw_only=True)
class TeamPlayers(BaseModel):
    players: list[Player]
    foreign_players: list[Player]
    national_players: list[Player]
    player_previous_teams: list[PlayerPreviousTeam]
