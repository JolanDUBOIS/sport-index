from __future__ import annotations

from datetime import datetime

from ..base import BaseModel, RawModel, ParsedModel
from ..primitives import Timestamp
from ..stage import RawStage, ParsedStage
from ..team import RawTeam, ParsedTeam


class RaceResults(BaseModel):
    position: int
    gridPosition: int
    points: int
    time: str               # Finishing time
    gap: str                # Gap to leader
    updatedAtTimestamp: int

class RawRaceResults(RaceResults, RawModel):
    stage: RawStage

class ParsedRaceResults(RaceResults, ParsedModel):
    stage: ParsedStage


class SeasonCareerHistory(BaseModel):
    position: int
    points: int
    victories: int
    racesStarted: int
    polePositions: int
    podiums: int

class RawSeasonCareerHistory(SeasonCareerHistory, RawModel):
    stage: RawStage
    parentTeam: RawTeam
    updatedAtTimestamp: Timestamp

class ParsedSeasonCareerHistory(SeasonCareerHistory, ParsedModel):
    stage: ParsedStage
    parentTeam: ParsedTeam
    updatedAtTimestamp: datetime


class TotalCareerHistory(BaseModel):
    racesStarted: int
    victories: int
    podiums: int
    polePositions: int
    worldChampionshipTitles: int

class RawTotalCareerHistory(TotalCareerHistory, RawModel):
    team: RawTeam

class ParsedTotalCareerHistory(TotalCareerHistory, ParsedModel):
    team: ParsedTeam


class DriverCareerHistory(BaseModel):
    pass

class RawDriverCareerHistory(DriverCareerHistory, RawModel):
    total: RawTotalCareerHistory
    bySeason: list[RawSeasonCareerHistory]

class ParsedDriverCareerHistory(DriverCareerHistory, ParsedModel):
    total: ParsedTotalCareerHistory
    bySeason: list[ParsedSeasonCareerHistory]


class Lap(BaseModel):
    """A single lap from a driver's race performance."""
    lap: int
    position: int
    tyreType: str
    visitedPitStop: bool


class DriverPerformance(BaseModel):
    id: int
    name: str
    slug: str
    startNumber: int
    laps: list[Lap]

class RawDriverPerformance(DriverPerformance, RawModel):
    parentTeam: RawTeam

class ParsedDriverPerformance(DriverPerformance, ParsedModel):
    parentTeam: ParsedTeam
