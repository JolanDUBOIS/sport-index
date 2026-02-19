from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .core import BaseModel, Sport, Country


@dataclass(frozen=True, kw_only=True)
class Cards(BaseModel):
    yellow: int
    red: int
    yellow_red: int

    @classmethod
    def _from_api(cls, raw: dict) -> Cards:
        return Cards(
            yellow=raw.get("yellowCards"),
            red=raw.get("redCards"),
            yellow_red=raw.get("yellowRedCards"),
        )

@dataclass(frozen=True, kw_only=True)
class Referee(BaseModel):
    id: str
    slug: str
    name: str
    games: int
    sport: Sport
    country: Country
    cards: Optional[Cards] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Referee:
        return Referee(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            games=raw.get("games"),
            sport=Sport.from_api(raw.get("sport")),
            country=Country.from_api(raw.get("country")),
            cards=Cards.from_api(raw) if any(key in raw for key in ["yellowCards", "redCards", "yellowRedCards"]) else None,
        )
