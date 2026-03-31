from __future__ import annotations

from typing import TYPE_CHECKING
from pydantic import Field

from .base import BaseSchema

if TYPE_CHECKING:
    from .player import _PlayerData


class Lineup(BaseSchema):
    formation: str | None = None
    players: list[_PlayerData] = Field(default_factory=list)
    missing_players: list[_PlayerData] = Field(default_factory=list)
