from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .category import Category
from .core import BaseModel, Country, Sport
from .event import Event
from .team import Team
from .tournament import UniqueTournament
from .utils import timestamp_to_iso, get_nested


@dataclass(frozen=True)
class RankingEntry(BaseModel):
    id: str
    position: int
    team: Team
    points: float
    country: Country
    previous_position: Optional[int] = None
    previous_points: Optional[float] = None
    last_event: Optional[Event] = None
    updated_at: Optional[str] = None

    @classmethod
    def _from_api(cls, raw: dict) -> RankingEntry:
        return RankingEntry(
            id=raw.get("id"),
            position=raw.get("position"),
            team=Team.from_api(raw.get("team")),
            points=raw.get("points"),
            country=Country.from_api(raw.get("country")),
            previous_position=raw.get("previousPosition"),
            previous_points=raw.get("previousPoints"),
            last_event=Event.from_api(raw.get("lastEvent")),
            updated_at=timestamp_to_iso(raw.get("updatedTimestamp")),
        )

@dataclass(frozen=True)
class Rankings(BaseModel):
    id: str
    slug: str
    name: str
    gender: str
    sport: Sport
    category: Category
    rankings: list[RankingEntry]
    unique_tournament: Optional[UniqueTournament] = None
    updated_at: Optional[str] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Rankings:
        return Rankings(
            id=get_nested(raw, "rankingType.id"),
            slug=get_nested(raw, "rankingType.slug"),
            name=get_nested(raw, "rankingType.name"),
            gender=get_nested(raw, "rankingType.gender"),
            sport=Sport.from_api(get_nested(raw, "rankingType.sport")),
            category=Category.from_api(get_nested(raw, "rankingType.category")),
            unique_tournament=UniqueTournament.from_api(get_nested(raw, "rankingType.uniqueTournament")),
            rankings=[RankingEntry.from_api(entry) for entry in raw.get("rankingRows", [])],
            updated_at=timestamp_to_iso(get_nested(raw, "rankingType.lastUpdatedTimestamp")),
        )
