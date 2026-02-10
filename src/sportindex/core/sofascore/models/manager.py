from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .core import BaseModel, Sport, Country, Performance
from .team import Team
from .utils import timestamp_to_iso


@dataclass(frozen=True)
class Manager(BaseModel):
    id: str
    slug: str
    name: str
    short_name: str
    team: Team
    teams: list[Team]
    sport: Sport
    country: Country
    deceased: Optional[bool] = None
    date_of_birth: Optional[str] = None
    performance: Optional[Performance] = None
    preferred_formation: Optional[str] = None
    former_player_id: Optional[str] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Manager:
        return Manager(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            short_name=raw.get("shortName"),
            team=Team.from_api(raw.get("team")),
            teams=[Team.from_api(t) for t in raw.get("teams", [])],
            sport=Sport.from_api(raw.get("sport")),
            country=Country.from_api({**raw.get("country", {}), "alpha3": raw.get("nationality")}),
            deceased=raw.get("deceased"),
            date_of_birth=timestamp_to_iso(raw.get("dateOfBirthTimestamp"), kind="date"),
            performance=Performance.from_api(raw.get("performance")),
            preferred_formation=raw.get("preferredFormation"),
            former_player_id=raw.get("formerPlayerId"),
        )
