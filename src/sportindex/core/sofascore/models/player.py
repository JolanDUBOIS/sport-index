from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .core import BaseModel, Country, Amount
from .team import Team
from .utils import timestamp_to_iso


@dataclass(frozen=True)
class Position(BaseModel):
    position: str
    detailed: Optional[list[str]] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Position:
        return Position(
            position=raw.get("position"),
            detailed=raw.get("positionsDetailed"),
        )

@dataclass(frozen=True)
class Player(BaseModel):
    id: str
    slug: str
    name: str
    short_name: str
    height: int
    gender: str
    number: int
    team: Team
    position: Position
    country: Country
    date_of_birth: Optional[str] = None
    retired: Optional[bool] = None
    deceased: Optional[bool] = None
    proposed_market_value: Optional[Amount] = None
    preferred_foot: Optional[str] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Player:
        return Player(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            short_name=raw.get("shortName"),
            height=raw.get("height"),
            gender=raw.get("gender"),
            date_of_birth=timestamp_to_iso(raw.get("dateOfBirthTimestamp"), kind="date"),
            number=raw.get("shirtNumber"),
            position=Position.from_api(raw),
            retired=raw.get("retired"),
            deceased=raw.get("deceased"),
            team=Team.from_api(raw.get("team")),
            country=Country.from_api(raw.get("country")),
            proposed_market_value=Amount.from_api(raw.get("proposedMarketValueRaw")),
            preferred_foot=raw.get("preferredFoot"),
        )
