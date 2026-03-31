from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import Field

from .base import BaseSchema

if TYPE_CHECKING:
    from .core import _SportData, _CountryData


class _RefereeData(BaseSchema):
    id: int
    slug: str
    name: str
    games: int | None = None
    sport: _SportData
    country: _CountryData | None = None
    yellow_cards: int | None = None
    red_cards: int | None = None
    yellow_red_cards: int | None = None
    dateOfBirth: datetime | None = Field(default=None, alias="dateOfBirthTimestamp")
