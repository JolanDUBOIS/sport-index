from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from .core import RawSport, RawCountry
    from .primitives import Timestamp, RawPerformance
    from .team import RawTeam


class RawManager(TypedDict, total=False):
    id: int
    slug: str
    name: str
    shortName: str
    sport: RawSport
    country: RawCountry
    nationality: str              # ISO3
    nationalityISO2: str          # ISO2
    deceased: bool
    performance: RawPerformance
    preferredFormation: str       # e.g. "4-3-3"
    formerPlayerId: int
    team: RawTeam
    teams: list[RawTeam]
    dateOfBirthTimestamp: Timestamp
