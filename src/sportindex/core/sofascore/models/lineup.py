from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass

from .core import BaseModel
from .player import Player


@dataclass(frozen=True)
class Lineup(BaseModel):
    players: List[Player]
    missing_players: Optional[List[Player]] = None
    formation: Optional[str] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Lineup:
        return Lineup(
            players=[Player.from_api(player) for player in raw.get("players", [])],
            missing_players=[Player.from_api(player) for player in raw.get("missingPlayers", [])],
            formation=raw.get("formation"),
        )

@dataclass(frozen=True)
class Lineups(BaseModel):
    home: Lineup
    away: Lineup

    @classmethod
    def _from_api(cls, raw: dict) -> Lineups:
        return Lineups(
            home=Lineup.from_api(raw.get("home")),
            away=Lineup.from_api(raw.get("away")),
        )
