from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from ..base import BaseParsedModel
from ..parsers import parse_timestamp, parse_iso
from sportindex.provider.raw.models import (
    RawTeamSeasonStats, RawTeamYearSurfaceStats,
    RawPlayerSeasonStatsItem, RawVenueStatistics
)
if TYPE_CHECKING:
    from ..team import ParsedTeam
    from ..player import ParsedPlayer
    from ..primitives import ParsedPerformance
    from ..tournament import ParsedUniqueTournament, ParsedSeason
    from sportindex.provider.raw.models import (
        RawPlayerPreviousTeam, RawTeamPlayers,
        RawPlayerSeasonStats, RawManagerCareerHistoryItem,
        RawTeamYearStats
    )


# =====================================================================
# Team Players
# =====================================================================

@dataclass
class ParsedPlayerPreviousTeam(BaseParsedModel):
    player: ParsedPlayer
    previousTeam: ParsedTeam
    transferDate: datetime

    @classmethod
    def _parse(cls, raw: RawPlayerPreviousTeam) -> ParsedPlayerPreviousTeam:
        from ..player import ParsedPlayer
        from ..team import ParsedTeam
        return cls(
            player=ParsedPlayer.from_raw(raw.get("player")),
            previousTeam=ParsedTeam.from_raw(raw.get("previousTeam")),
            transferDate=parse_iso(raw.get("transferDate"))
        )


@dataclass
class ParsedTeamPlayers(BaseParsedModel):
    players: list[ParsedPlayer]
    foreignPlayers: list[ParsedPlayer]
    nationalPlayers: list[ParsedPlayer]
    playerPreviousTeams: list[ParsedPlayerPreviousTeam]

    @classmethod
    def _parse(cls, raw: RawTeamPlayers) -> ParsedTeamPlayers:
        from ..player import ParsedPlayer
        return cls(
            players=[ParsedPlayer.from_raw(p) for p in raw.get("players", [])],
            foreignPlayers=[ParsedPlayer.from_raw(p) for p in raw.get("foreignPlayers", [])],
            nationalPlayers=[ParsedPlayer.from_raw(p) for p in raw.get("nationalPlayers", [])],
            playerPreviousTeams=[ParsedPlayerPreviousTeam.from_raw(t) for t in raw.get("playerPreviousTeams", [])]
        )


# =====================================================================
# Team Season Stats
# =====================================================================

@dataclass
class ParsedTeamSeasonStats(BaseParsedModel):
    __annotations__ = RawTeamSeasonStats.__annotations__

    @classmethod
    def _parse(cls, raw: RawTeamSeasonStats) -> ParsedTeamSeasonStats:
        return cls(**raw)


# =====================================================================
# Team Year Stats (Tennis)
# =====================================================================

@dataclass
class ParsedTeamYearSurfaceStats(BaseParsedModel):
    __annotations__ = RawTeamYearSurfaceStats.__annotations__

    @classmethod
    def _parse(cls, raw: RawTeamYearSurfaceStats) -> ParsedTeamYearSurfaceStats:
        return cls(**raw)


@dataclass
class ParsedTeamYearStats(BaseParsedModel):
    statistics: list[ParsedTeamYearSurfaceStats]

    @classmethod
    def _parse(cls, raw: RawTeamYearStats) -> ParsedTeamYearStats:
        return cls(statistics=[ParsedTeamYearSurfaceStats.from_raw(stat) for stat in raw.get("statistics", [])])


# =====================================================================
# Player Statistics
# =====================================================================

@dataclass
class ParsedPlayerSeasonStatsItem(BaseParsedModel):
    __annotations__ = RawPlayerSeasonStatsItem.__annotations__

    @classmethod
    def _parse(cls, raw: RawPlayerSeasonStatsItem) -> ParsedPlayerSeasonStatsItem:
        return cls(**raw)


@dataclass
class ParsedPlayerSeasonStats(BaseParsedModel):
    year: str
    startYear: int
    endYear: int
    statistics: ParsedPlayerSeasonStatsItem
    team: ParsedTeam
    uniqueTournament: ParsedUniqueTournament
    season: ParsedSeason

    @classmethod
    def _parse(cls, raw: RawPlayerSeasonStats) -> ParsedPlayerSeasonStats:
        from ..team import ParsedTeam
        from ..tournament import ParsedUniqueTournament, ParsedSeason
        return cls(
            year=raw.get("year"),
            startYear=raw.get("startYear"),
            endYear=raw.get("endYear"),
            statistics=ParsedPlayerSeasonStatsItem.from_raw(raw.get("statistics")),
            team=ParsedTeam.from_raw(raw.get("team")),
            uniqueTournament=ParsedUniqueTournament.from_raw(raw.get("uniqueTournament")),
            season=ParsedSeason.from_raw(raw.get("season"))
        )


# =====================================================================
# Manager Career History
# =====================================================================

@dataclass
class ParsedManagerCareerHistoryItem(BaseParsedModel):
    performance: ParsedPerformance
    team: ParsedTeam
    start: datetime
    end: datetime

    @classmethod
    def _parse(cls, raw: RawManagerCareerHistoryItem) -> ParsedManagerCareerHistoryItem:
        from ..primitives import ParsedPerformance
        from ..team import ParsedTeam
        return cls(
            performance=ParsedPerformance.from_raw(raw.get("performance")),
            team=ParsedTeam.from_raw(raw.get("team")),
            start=parse_timestamp(raw.get("startTimestamp")),
            end=parse_timestamp(raw.get("endTimestamp"))
        )


# =====================================================================
# Venue Statistics
# =====================================================================

@dataclass
class ParsedVenueStatistics(BaseParsedModel):
    __annotations__ = RawVenueStatistics.__annotations__

    @classmethod
    def _parse(cls, raw: RawVenueStatistics) -> ParsedVenueStatistics:
        return cls(**raw)
