from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from .core import RawSport, RawCountry
    from .primitives import Timestamp


class RawReferee(TypedDict, total=False):
    id: int
    slug: str
    name: str
    games: int
    sport: RawSport
    country: RawCountry
    yellowCards: int
    redCards: int
    yellowRedCards: int
    dateOfBirthTimestamp: Timestamp
