from __future__ import annotations

from datetime import datetime
from typing import Literal, TYPE_CHECKING, Any

from pydantic import Field, ValidationInfo, model_validator

from .base import BaseSchema

if TYPE_CHECKING:
    from .core import _CountryData
    from .primitives import Amount
    from .team import _TeamData


class _PlayerData(BaseSchema):
    id: int
    slug: str
    name: str
    first_name: str | None = None
    last_name: str | None = None
    short_name: str | None = None
    gender: str | None = None                  # "M", "F", "X"
    country: _CountryData | None = None
    weight: int | None = None                  # in kg
    height: int | None = None                  # in cm
    shirt_number: int | None = None
    status: str | None = None                  # e.g. "Active", "Retired"
    retired: bool | None = None
    deceased: bool | None = None
    preferred_foot: str | None = None
    preferred_hand: str | None = None
    salary: Amount | None = Field(default=None, alias="salaryRaw")
    proposed_market_value: Amount | None = Field(default=None, alias="proposedMarketValueRaw")
    position: str | None = None                # e.g. "G", "D", "M", "F"
    positions_detailed: list[str] | None = None # e.g. ["RW", "ST"]
    primary_position: str | None = None
    team: _TeamData | None = None
    date_of_birth: datetime | None = Field(default=None, alias="dateOfBirthTimestamp")
    contract_until: datetime | None = Field(default=None, alias="contractUntilTimestamp")
    role: Literal["player"] = Field(default="player")


class PlayerPreviousTeam(BaseSchema):
    player: _PlayerData
    previous_team: _TeamData
    transfer_date: datetime


class TeamPlayers(BaseSchema):
    players: list[_PlayerData] = Field(default_factory=list)
    foreign_players: list[_PlayerData] = Field(default_factory=list)
    national_players: list[_PlayerData] = Field(default_factory=list)
    player_previous_teams: list[PlayerPreviousTeam] = Field(default_factory=list)

    @model_validator(mode='before')
    @classmethod
    def unwrap_player_shells(cls, data: Any, info: ValidationInfo) -> Any:
        if not isinstance(data, dict):
            return data

        if info.context and info.context.get("preprocessed"):
            return data

        list_keys = ["players", "nationalPlayers", "foreignPlayers", "playerPreviousTeams"]

        for key in list_keys:
            if key in data and isinstance(data[key], list):
                unwrapped_list = []
                for item in data[key]:
                    if isinstance(item, dict) and "player" in item:
                        unwrapped_list.append(item["player"])
                    else:
                        unwrapped_list.append(item)
                
                data[key] = unwrapped_list

        return data

