from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import TYPE_CHECKING

from pydantic import Field

from .base import BaseSchema

if TYPE_CHECKING:
    from .core import _CategoryData, _CountryData, _SportData
    from .manager import _ManagerData
    from .primitives import Amount
    from .tournament import _TournamentData, _UniqueTournamentData
    from .venue import _VenueData


# ===========================================================================
# Player Team Info
# ===========================================================================

class _PlayerTeamInfoData(BaseSchema):
    id: int
    residence: str | None = None
    birthplace: str | None = None
    height: float | None = None        # in m (e.g. 1.85)
    weight: float | None = None        # in kg
    number: int | None = None
    plays: str | None = None           # e.g. "right-handed"
    main_driver: bool | None = None
    turned_pro: str | None = None       # e.g. "2018"
    prize_current: Amount | None = Field(default=None, alias="prizeCurrentRaw")
    prize_total: Amount | None = Field(default=None, alias="prizeTotalRaw")
    current_ranking: int | None = None
    birth_date: datetime | None = Field(default=None, alias="birthDateTimestamp")


# ===========================================================================
# Team
# ===========================================================================

class _TeamData(BaseSchema):
    id: int
    slug: str
    name: str
    short_name: str | None = None
    full_name: str | None = None
    name_code: str | None = None        # e.g. "PSG", "BAR"
    gender: str | None = None          # "M", "F"
    sport: _SportData
    category: _CategoryData | None = None
    country: _CountryData | None = None
    national: bool | None = None
    disabled: bool | None = None
    ranking: int | None = None
    tournament: _TournamentData | None = None
    primary_unique_tournament: _UniqueTournamentData | None = None
    manager: _ManagerData | None = None
    venue: _VenueData | None = None
    foundation_date: datetime | None = Field(default=None, alias="foundationDateTimestamp")
    parent_team: _TeamData | None = None
    player_team_info: _PlayerTeamInfoData | None = None
