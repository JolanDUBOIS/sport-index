from datetime import datetime

from .base import BaseModel, RawModel, ParsedModel
from .common import Country
from .primitives import Timestamp, Amount
from .team import RawTeam, ParsedTeam


class Player(BaseModel):
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

class RawPlayer(Player, RawModel):
    team: RawTeam
    dateOfBirthTimestamp: Timestamp
    contractUntilTimestamp: Timestamp

class ParsedPlayer(Player, ParsedModel):
    team: ParsedTeam
    dateOfBirthTimestamp: datetime
    contractUntilTimestamp: datetime
