from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from .category import Category
from .core import BaseModel, Country, Sport
from .utils import timestamp_to_iso
if TYPE_CHECKING:
    from .manager import Manager
    from .venue import Venue


@dataclass(frozen=True)
class Team(BaseModel):
    id: str
    slug: str
    name: str
    short_name: str
    full_name: str
    name_code: str
    national: bool
    gender: str
    country: Country
    category: Category
    sport: Sport
    manager: Optional[Manager] = None
    parent: Optional[Team] = None
    venue: Optional[Venue] = None
    ranking: Optional[int] = None
    founded: Optional[int] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Team:
        from .manager import Manager # Avoid circular imports
        from .venue import Venue # Avoid circular imports
        return Team(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            short_name=raw.get("shortName"),
            full_name=raw.get("fullName"),
            name_code=raw.get("nameCode"),
            national=raw.get("national"),
            gender=raw.get("gender"),
            country=Country.from_api(raw.get("country")),
            category=Category.from_api(raw.get("category")),
            sport=Sport.from_api(raw.get("sport")),
            manager=Manager.from_api(raw.get("manager")),
            parent=Team.from_api(raw.get("parentTeam")),
            venue=Venue.from_api(raw.get("venue")),
            ranking=raw.get("ranking"),
            founded=timestamp_to_iso(raw.get("foundationDateTimestamp"), kind="date"),
        )

# Note - Additional keys:
# - pregameForm.form
# - wdlRecords (MMA)
# - tournament & primaryUniqueTournament (~main league)