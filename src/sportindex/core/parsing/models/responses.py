from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from .base import BaseParsedModel
if TYPE_CHECKING:
    from .details import ParsedLineup
    from .event import ParsedEvent
    from .leaderboard import ParsedRankingType, ParsedRankingEntry
    from .stage import ParsedStage
    from .team import ParsedTeam
    from .tournament import ParsedUniqueTournament, ParsedSeason
    from sportindex.core.provider.models import (
        TeamResponse, UniqueTournamentSeasonsResponse,
        EventsResponse, RankingsResponse,
        ChannelScheduleResponse, LineupsResponse,
        Channel
    )


@dataclass
class ParsedTeamResponse(BaseParsedModel):
    team: ParsedTeam
    relatedTeams: list[ParsedTeam]
    drivers: list[ParsedTeam]

    @classmethod
    def _parse(cls, raw: TeamResponse) -> ParsedTeamResponse:
        from .team import ParsedTeam
        return cls(
            team=ParsedTeam.from_raw(raw.get("team")),
            relatedTeams=[ParsedTeam.from_raw(rt) for rt in raw.get("relatedTeams", [])],
            drivers=[ParsedTeam.from_raw(d) for d in raw.get("drivers", [])],
        )


@dataclass
class ParsedUniqueTournamentSeasonsResponse(BaseParsedModel):
    uniqueTournament: ParsedUniqueTournament
    seasons: list[ParsedSeason]

    @classmethod
    def _parse(cls, raw: UniqueTournamentSeasonsResponse) -> ParsedUniqueTournamentSeasonsResponse:
        from .tournament import ParsedUniqueTournament, ParsedSeason
        return cls(
            uniqueTournament=ParsedUniqueTournament.from_raw(raw.get("uniqueTournament")),
            seasons=[ParsedSeason.from_raw(s) for s in raw.get("seasons", [])],
        )


@dataclass
class ParsedEventsResponse(BaseParsedModel):
    hasNextPage: bool
    events: list[ParsedEvent]

    @classmethod
    def _parse(cls, raw: EventsResponse) -> ParsedEventsResponse:
        from .event import ParsedEvent
        return cls(
            hasNextPage=raw.get("hasNextPage"),
            events=[ParsedEvent.from_raw(e) for e in raw.get("events", [])],
        )


@dataclass
class ParsedRankingsResponse(BaseParsedModel):
    rankingType: ParsedRankingType
    rankingRows: list[ParsedRankingEntry]

    @classmethod
    def _parse(cls, raw: RankingsResponse) -> ParsedRankingsResponse:
        from .leaderboard import ParsedRankingType, ParsedRankingEntry
        return cls(
            rankingType=ParsedRankingType.from_raw(raw.get("rankingType")),
            rankingRows=[ParsedRankingEntry.from_raw(r) for r in raw.get("rankingRows", [])],
        )


@dataclass
class ParsedChannelScheduleResponse(BaseParsedModel):
    channel: Channel
    events: list[ParsedEvent]
    stages: list[ParsedStage]

    @classmethod
    def _parse(cls, raw: ChannelScheduleResponse) -> ParsedChannelScheduleResponse:
        from .event import ParsedEvent
        from .stage import ParsedStage
        return cls(
            channel=raw.get("channel"),
            events=[ParsedEvent.from_raw(e) for e in raw.get("events", [])],
            stages=[ParsedStage.from_raw(s) for s in raw.get("stages", [])],
        )


@dataclass
class ParsedLineupsResponse(BaseParsedModel):
    home: ParsedLineup
    away: ParsedLineup

    @classmethod
    def _parse(cls, raw: LineupsResponse) -> ParsedLineupsResponse:
        from .details import ParsedLineup
        return cls(
            home=ParsedLineup.from_raw(raw.get("home")),
            away=ParsedLineup.from_raw(raw.get("away")),
        )
