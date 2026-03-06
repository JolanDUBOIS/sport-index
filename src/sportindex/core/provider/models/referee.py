from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from .main import Sport, Country
    from .primitives import Timestamp


class Referee(TypedDict, total=False):
    id: int
    slug: str
    name: str
    games: int
    sport: Sport
    country: Country
    yellowCards: int
    redCards: int
    yellowRedCards: int
    dateOfBirthTimestamp: Timestamp
