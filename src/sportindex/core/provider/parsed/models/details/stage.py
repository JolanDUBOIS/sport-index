from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from ..base import BaseParsedModel
from ..parsers import parse_timestamp
if TYPE_CHECKING:
    from ..stage import ParsedStage
    from ..team import ParsedTeam
    from sportindex.core.provider.raw.models import (
        RaceResults, SeasonCareerHistory,
        TotalCareerHistory, DriverCareerHistory,
        DriverPerformance, Lap
    )


@dataclass
class ParsedRaceResults(BaseParsedModel):
    position: int
    gridPosition: int
    points: int
    time: str               # Finishing time
    gap: str                # Gap to leader
    updatedAtTimestamp: int
    stage: ParsedStage

    @classmethod
    def _parse(cls, raw: RaceResults) -> ParsedRaceResults:
        from ..stage import ParsedStage
        return cls(
            position=raw.get("position"),
            gridPosition=raw.get("gridPosition"),
            points=raw.get("points"),
            time=raw.get("time"),
            gap=raw.get("gap"),
            updatedAtTimestamp=parse_timestamp(raw.get("updatedAtTimestamp")),
            stage=ParsedStage.from_raw(raw.get("stage"))
        )


@dataclass
class ParsedSeasonCareerHistory(BaseParsedModel):
    position: int
    points: int
    victories: int
    racesStarted: int
    polePositions: int
    podiums: int
    stage: ParsedStage
    parentTeam: ParsedTeam
    updatedAtTimestamp: datetime

    @classmethod
    def _parse(cls, raw: SeasonCareerHistory) -> ParsedSeasonCareerHistory:
        from ..stage import ParsedStage
        from ..team import ParsedTeam
        return cls(
            position=raw.get("position"),
            points=raw.get("points"),
            victories=raw.get("victories"),
            racesStarted=raw.get("racesStarted"),
            polePositions=raw.get("polePositions"),
            podiums=raw.get("podiums"),
            stage=ParsedStage.from_raw(raw.get("stage")),
            parentTeam=ParsedTeam.from_raw(raw.get("parentTeam")),
            updatedAtTimestamp=parse_timestamp(raw.get("updatedAtTimestamp"))
        )


@dataclass
class ParsedTotalCareerHistory(BaseParsedModel):
    racesStarted: int
    victories: int
    podiums: int
    polePositions: int
    worldChampionshipTitles: int
    team: ParsedTeam

    @classmethod
    def _parse(cls, raw: TotalCareerHistory) -> ParsedTotalCareerHistory:
        from ..team import ParsedTeam
        return cls(
            racesStarted=raw.get("racesStarted"),
            victories=raw.get("victories"),
            podiums=raw.get("podiums"),
            polePositions=raw.get("polePositions"),
            worldChampionshipTitles=raw.get("worldChampionshipTitles"),
            team=ParsedTeam.from_raw(raw.get("team"))
        )


@dataclass
class ParsedDriverCareerHistory(BaseParsedModel):
    total: ParsedTotalCareerHistory
    bySeason: list[ParsedSeasonCareerHistory]


    @classmethod
    def _parse(cls, raw: DriverCareerHistory) -> ParsedDriverCareerHistory:
        return cls(
            total=ParsedTotalCareerHistory.from_raw(raw.get("total")),
            bySeason=[ParsedSeasonCareerHistory.from_raw(season) for season in raw.get("bySeason")]
        )


@dataclass
class ParsedDriverPerformance(BaseParsedModel):
    id: int
    name: str
    slug: str
    startNumber: int
    laps: list[Lap]
    parentTeam: ParsedTeam

    @classmethod
    def _parse(cls, raw: DriverPerformance) -> ParsedDriverPerformance:
        from ..team import ParsedTeam
        return cls(
            id=raw.get("id"),
            name=raw.get("name"),
            slug=raw.get("slug"),
            startNumber=raw.get("startNumber"),
            laps=raw.get("laps", []),
            parentTeam=ParsedTeam.from_raw(raw.get("parentTeam"))
        )
