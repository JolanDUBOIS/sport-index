from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from ..parsers import parse_timestamp, parse_iso
if TYPE_CHECKING:
    from ..team import ParsedTeam
    from ..player import ParsedPlayer
    from ..tournament import ParsedUniqueTournament, ParsedSeason
    from sportindex.core.provider.models import (
        PlayerPreviousTeam, TeamPlayers,
        PlayerSeasonStats, ManagerCareerHistoryItem,
        PlayerSeasonStatsItem, Performance
    )


# =====================================================================
# Team Players
# =====================================================================

@dataclass
class ParsedPlayerPreviousTeam:
    player: ParsedPlayer
    previousTeam: ParsedTeam
    transferDate: datetime

    @classmethod
    def from_raw(cls, raw: PlayerPreviousTeam) -> ParsedPlayerPreviousTeam:
        from ..player import ParsedPlayer
        from ..team import ParsedTeam
        return cls(
            player=ParsedPlayer.from_raw(raw.get("player")),
            previousTeam=ParsedTeam.from_raw(raw.get("previousTeam")),
            transferDate=parse_iso(raw.get("transferDate"))
        )


@dataclass
class ParsedTeamPlayers:
    players: list[ParsedPlayer]
    foreignPlayers: list[ParsedPlayer]
    nationalPlayers: list[ParsedPlayer]
    playerPreviousTeams: list[ParsedPlayerPreviousTeam]

    @classmethod
    def from_raw(cls, raw: TeamPlayers) -> ParsedTeamPlayers:
        from ..player import ParsedPlayer
        from ..team import ParsedTeam
        from ..tournament import ParsedUniqueTournament, ParsedSeason
        return cls(
            players=[ParsedPlayer.from_raw(p) for p in raw.get("players", [])],
            foreignPlayers=[ParsedPlayer.from_raw(p) for p in raw.get("foreignPlayers", [])],
            nationalPlayers=[ParsedPlayer.from_raw(p) for p in raw.get("nationalPlayers", [])],
            playerPreviousTeams=[ParsedPlayerPreviousTeam.from_raw(t) for t in raw.get("playerPreviousTeams", [])]
        )


# =====================================================================
# Player Statistics
# =====================================================================

@dataclass
class ParsedPlayerSeasonStats:
    year: str
    startYear: int
    endYear: int
    statistics: PlayerSeasonStatsItem
    team: ParsedTeam
    uniqueTournament: ParsedUniqueTournament
    season: ParsedSeason

    @classmethod
    def from_raw(cls, raw: PlayerSeasonStats) -> ParsedPlayerSeasonStats:
        from ..team import ParsedTeam
        from ..tournament import ParsedUniqueTournament, ParsedSeason
        return cls(
            year=raw.get("year"),
            startYear=raw.get("startYear"),
            endYear=raw.get("endYear"),
            statistics=raw.get("statistics"),
            team=ParsedTeam.from_raw(raw.get("team")),
            uniqueTournament=ParsedUniqueTournament.from_raw(raw.get("uniqueTournament")),
            season=ParsedSeason.from_raw(raw.get("season"))
        )


# =====================================================================
# Manager Career History
# =====================================================================

@dataclass
class ParsedManagerCareerHistoryItem:
    performance: Performance
    team: ParsedTeam
    startTimestamp: datetime
    endTimestamp: datetime

    @classmethod
    def from_raw(cls, raw: ManagerCareerHistoryItem) -> ParsedManagerCareerHistoryItem:
        from ..team import ParsedTeam
        return cls(
            performance=raw.get("performance"),
            team=ParsedTeam.from_raw(raw.get("team")),
            startTimestamp=parse_timestamp(raw.get("startTimestamp")),
            endTimestamp=parse_timestamp(raw.get("endTimestamp"))
        )