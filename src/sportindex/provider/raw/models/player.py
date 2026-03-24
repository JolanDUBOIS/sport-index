from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from .core import RawCountry
    from .primitives import Timestamp, RawAmount
    from .team import RawTeam


class RawPlayer(TypedDict, total=False):
    id: int
    slug: str
    name: str
    firstName: str
    lastName: str
    shortName: str
    gender: str                  # "M", "F", "X"
    country: RawCountry
    weight: int                  # in kg
    height: int                  # in cm
    shirtNumber: int
    status: str                  # e.g. "Active", "Retired"
    retired: bool
    deceased: bool
    preferredFoot: str
    preferredHand: str           # Never seen this field populated, but it might exist...
    salaryRaw: RawAmount
    proposedMarketValueRaw: RawAmount
    position: str                # e.g. "G", "D", "M", "F"
    positionsDetailed: list[str] # e.g. ["RW", "ST"]
    primaryPosition: str
    team: RawTeam
    dateOfBirthTimestamp: Timestamp
    contractUntilTimestamp: Timestamp
