from datetime import datetime

from .base import BaseModel, RawModel, ParsedModel
from .common import Sport, Country
from .primitives import Timestamp


class Referee(BaseModel):
    id: int
    slug: str
    name: str
    games: int
    sport: Sport
    country: Country
    yellowCards: int
    redCards: int
    yellowRedCards: int

class RawReferee(Referee, RawModel):
    dateOfBirthTimestamp: Timestamp

class ParsedReferee(Referee, ParsedModel):
    dateOfBirthTimestamp: datetime
