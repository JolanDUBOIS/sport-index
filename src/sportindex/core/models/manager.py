from datetime import datetime

from typing import TYPE_CHECKING
from datetime import datetime

from .base import BaseModel, RawModel, ParsedModel
from .common import Sport, Country
from .primitives import Timestamp, Performance

if TYPE_CHECKING:
    from .team import RawTeam, ParsedTeam


class Manager(BaseModel):
    id: int
    slug: str
    name: str
    shortName: str
    sport: Sport
    country: Country
    nationality: str              # ISO3
    nationalityISO2: str          # ISO2
    deceased: bool
    performance: Performance
    preferredFormation: str       # e.g. "4-3-3"
    formerPlayerId: int

class RawManager(Manager, RawModel):
    team: RawTeam
    teams: list[RawTeam]
    dateOfBirthTimestamp: Timestamp

class ParsedManager(Manager, ParsedModel):
    team: ParsedTeam
    teams: list[ParsedTeam]
    dateOfBirthTimestamp: datetime
