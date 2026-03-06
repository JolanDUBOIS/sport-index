from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from .base import BaseParsedModel
from .parsers import parse_timestamp
if TYPE_CHECKING:
    from .team import ParsedTeam
    from sportindex.core.provider.models import (
        StageParent, UniqueStage,
        StageType, Status, Stage,
        Country, StageInfo
    )


@dataclass
class ParsedStageParent(BaseParsedModel):
    id: int
    slug: str
    description: str
    startDateTimestamp: datetime

    @classmethod
    def _parse(cls, raw: StageParent) -> ParsedStageParent:
        return cls(
            id=raw.get("id"),
            slug=raw.get("slug"),
            description=raw.get("description"),
            startDateTimestamp=parse_timestamp(raw.get("startDateTimestamp"))
        )


@dataclass
class ParsedStage(BaseParsedModel):
    id: int
    slug: str
    name: str
    description: str
    year: str
    seasonStageName: str
    uniqueStage: UniqueStage
    type: StageType
    status: Status
    flag: str
    country: Country
    info: StageInfo
    startDateTimestamp: datetime
    endDateTimestamp: datetime
    stageParent: ParsedStageParent
    winner: ParsedTeam
    substages: list[ParsedStage]

    @classmethod
    def _parse(cls, raw: Stage) -> ParsedStage:
        from .team import ParsedTeam
        return cls(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            description=raw.get("description"),
            year=raw.get("year"),
            seasonStageName=raw.get("seasonStageName"),
            uniqueStage=raw.get("uniqueStage"),
            type=raw.get("type"),
            status=raw.get("status"),
            flag=raw.get("flag"),
            country=raw.get("country"),
            info=raw.get("info"),
            startDateTimestamp=parse_timestamp(raw.get("startDateTimestamp")),
            endDateTimestamp=parse_timestamp(raw.get("endDateTimestamp")),
            stageParent=ParsedStageParent.from_raw(raw.get("stageParent")),
            winner=ParsedTeam.from_raw(raw.get("winner")),
            substages=[cls.from_raw(s) for s in raw.get("substages", [])]
        )
