from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from .base import BaseParsedModel
from .parsers import parse_timestamp
if TYPE_CHECKING:
    from .core import ParsedCountry
    from .team import ParsedTeam
    from sportindex.core.provider.raw.models import Player, Amount


@dataclass
class ParsedPlayer(BaseParsedModel):
    id: int
    slug: str
    name: str
    firstName: str
    lastName: str
    shortName: str
    gender: str                  # "M", "F", "X"
    country: ParsedCountry
    weight: int                  # in kg
    height: int                  # in cm
    shirtNumber: int
    status: str                  # e.g. "Active", "Retired"
    retired: bool
    deceased: bool
    preferredFoot: str
    preferredHand: str
    salaryRaw: Amount
    proposedMarketValueRaw: Amount
    position: str                # e.g. "G", "D", "M", "F"
    positionsDetailed: list[str] # e.g. ["RW", "ST"]
    primaryPosition: str
    team: ParsedTeam
    dateOfBirth: datetime
    contractUntil: datetime

    @classmethod
    def _parse(cls, raw: Player) -> ParsedPlayer:
        from .core import ParsedCountry
        from .team import ParsedTeam
        return cls(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            firstName=raw.get("firstName"),
            lastName=raw.get("lastName"),
            shortName=raw.get("shortName"),
            gender=raw.get("gender"),
            country=ParsedCountry.from_raw(raw.get("country")),
            weight=raw.get("weight"),
            height=raw.get("height"),
            shirtNumber=raw.get("shirtNumber"),
            status=raw.get("status"),
            retired=raw.get("retired"),
            deceased=raw.get("deceased"),
            preferredFoot=raw.get("preferredFoot"),
            preferredHand=raw.get("preferredHand"),
            salaryRaw=raw.get("salaryRaw"),
            proposedMarketValueRaw=raw.get("proposedMarketValueRaw"),
            position=raw.get("position"),
            positionsDetailed=raw.get("positionsDetailed"),
            primaryPosition=raw.get("primaryPosition"),
            team=ParsedTeam.from_raw(raw.get("team")),
            dateOfBirth=parse_timestamp(raw.get("dateOfBirthTimestamp")),
            contractUntil=parse_timestamp(raw.get("contractUntilTimestamp"))
        )
