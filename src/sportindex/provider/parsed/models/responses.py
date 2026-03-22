from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import BaseParsedModel
if TYPE_CHECKING:
    from .details import ParsedLineup
    from .event import ParsedEvent
    from .leaderboard import ParsedRankingType, ParsedRankingEntry
    from .primitives import ParsedChannel
    from .stage import ParsedStage
    from .team import ParsedTeam
    from .tournament import ParsedUniqueTournament, ParsedSeason
    from sportindex.provider.raw.models import (
        TeamResponse, UniqueTournamentSeasonsResponse,
        EventsResponse, RankingsResponse,
        ChannelScheduleResponse, LineupsResponse,
        PeriodStatistics, MomentumPoint,
        CountryChannelsResponse, EventStatisticsResponse,
        MomentumGraphResponse, ChannelEventVotesResponse
    )


# =====================================================================
# Team
# =====================================================================

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


# =====================================================================
# Tournament
# =====================================================================

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


# =====================================================================
# Event
# =====================================================================

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


# =====================================================================
# Leaderboard
# =====================================================================

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


# =====================================================================
# Channel / TV
# =====================================================================

@dataclass
class ParsedChannelScheduleResponse(BaseParsedModel):
    channel: ParsedChannel
    events: list[ParsedEvent]
    stages: list[ParsedStage]

    @classmethod
    def _parse(cls, raw: ChannelScheduleResponse) -> ParsedChannelScheduleResponse:
        from .event import ParsedEvent
        from .primitives import ParsedChannel
        from .stage import ParsedStage
        return cls(
            channel=ParsedChannel.from_raw(raw.get("channel")),
            events=[ParsedEvent.from_raw(e) for e in raw.get("events", [])],
            stages=[ParsedStage.from_raw(s) for s in raw.get("stages", [])],
        )


@dataclass
class ParsedCountryChannelsResponse(BaseParsedModel):
    channels: dict[str, list[int]]

    @classmethod
    def _parse(cls, raw: CountryChannelsResponse) -> ParsedCountryChannelsResponse:
        return cls(channels=raw.get("channels", {}))


@dataclass
class ParsedChannelEventVotesResponse(BaseParsedModel):
    channel: ParsedChannel
    upvotes: int
    downvotes: int

    @classmethod
    def _parse(cls, raw: ChannelEventVotesResponse) -> ParsedChannelEventVotesResponse:
        from .primitives import ParsedChannel
        return cls(
            channel=ParsedChannel.from_raw(raw.get("tvChannel")),
            upvotes=raw.get("upvote", 0),
            downvotes=raw.get("downvote", 0),
        )


# =====================================================================
# Event Details
# =====================================================================

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


@dataclass
class ParsedEventStatisticsResponse(BaseParsedModel):
    statistics: list[PeriodStatistics]

    @classmethod
    def _parse(cls, raw: EventStatisticsResponse) -> ParsedEventStatisticsResponse:
        return cls(statistics=raw.get("statistics", []))


@dataclass
class ParsedMomentumGraphResponse(BaseParsedModel):
    graphPoints: list[MomentumPoint]
    periodTime: int
    periodCount: int
    overtimeLength: int

    @classmethod
    def _parse(cls, raw: MomentumGraphResponse) -> ParsedMomentumGraphResponse:
        return cls(**raw.values())
