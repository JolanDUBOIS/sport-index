from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from .main import Country
    from .primitives import Timestamp, Amount
    from .team import Team


class Player(TypedDict, total=False):
    id: int
    slug: str
    name: str
    firstName: str
    lastName: str
    shortName: str
    gender: str                  # "M", "F", "X"
    country: Country
    weight: int                  # in kg
    height: int                  # in cm
    shirtNumber: int
    status: str                  # e.g. "Active", "Retired"
    retired: bool
    deceased: bool
    preferredFoot: str
    salaryRaw: Amount
    proposedMarketValueRaw: Amount
    position: str                # e.g. "G", "D", "M", "F"
    positionsDetailed: list[str] # e.g. ["RW", "ST"]
    primaryPosition: str
    team: Team
    dateOfBirthTimestamp: Timestamp
    contractUntilTimestamp: Timestamp
