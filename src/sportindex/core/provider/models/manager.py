from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING


if TYPE_CHECKING:
    from .main import Sport, Country
    from .primitives import Timestamp, Performance
    from .team import Team


class Manager(TypedDict, total=False):
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
    team: Team
    teams: list[Team]
    dateOfBirthTimestamp: Timestamp
