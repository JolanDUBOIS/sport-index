from .base import BaseModel, RawModel, ParsedModel
from .details import RawLineup, ParsedLineup, MomentumPoint, PeriodStatistics
from .event import RawEvent, ParsedEvent
from .leaderboard import RawRankingEntry, ParsedRankingEntry, RawRankingType, ParsedRankingType
from .primitives import Channel
from .stage import RawStage, ParsedStage
from .team import RawTeam, ParsedTeam
from .tournament import RawSeason, ParsedSeason, RawUniqueTournament, ParsedUniqueTournament


# =====================================================================
# Team
# =====================================================================

class TeamResponse(BaseModel):
    pass

class RawTeamResponse(TeamResponse, RawModel):
    team: RawTeam
    relatedTeams: list[RawTeam]
    drivers: list[RawTeam]

class ParsedTeamResponse(TeamResponse, ParsedModel):
    team: ParsedTeam
    relatedTeams: list[ParsedTeam]
    drivers: list[ParsedTeam]


# =====================================================================
# Tournament
# =====================================================================

class UniqueTournamentSeasonsResponse(BaseModel):
    pass

class RawUniqueTournamentSeasonsResponse(UniqueTournamentSeasonsResponse, RawModel):
    uniqueTournament: RawUniqueTournament
    seasons: list[RawSeason]

class ParsedUniqueTournamentSeasonsResponse(UniqueTournamentSeasonsResponse, ParsedModel):
    uniqueTournament: ParsedUniqueTournament
    seasons: list[ParsedSeason]


# =====================================================================
# Event
# =====================================================================

class EventsResponse(BaseModel):
    hasNextPage: bool

class RawEventsResponse(EventsResponse, RawModel):
    events: list[RawEvent]

class ParsedEventsResponse(EventsResponse, ParsedModel):
    events: list[ParsedEvent]


# =====================================================================
# Leaderboard
# =====================================================================

class RankingsResponse(BaseModel):
    pass

class RawRankingsResponse(RankingsResponse, RawModel):
    rankingType: RawRankingType
    rankingRows: list[RawRankingEntry]

class ParsedRankingsResponse(RankingsResponse, ParsedModel):
    rankingType: ParsedRankingType
    rankingRows: list[ParsedRankingEntry]


# =====================================================================
# Channel / TV
# =====================================================================

class ChannelScheduleResponse(BaseModel):
    channel: Channel

class RawChannelScheduleResponse(ChannelScheduleResponse, RawModel):
    events: list[RawEvent]
    stages: list[RawStage]

class ParsedChannelScheduleResponse(ChannelScheduleResponse, ParsedModel):
    events: list[ParsedEvent]
    stages: list[ParsedStage]


class CountryChannelsResponse(BaseModel):
    channels: dict[str, list[int]]


# =====================================================================
# Event Details
# =====================================================================

class LineupsResponse(BaseModel):
    pass

class RawLineupsResponse(LineupsResponse, RawModel):
    home: RawLineup
    away: RawLineup

class ParsedLineupsResponse(LineupsResponse, ParsedModel):
    home: ParsedLineup
    away: ParsedLineup


class EventStatisticsResponse(BaseModel):
    statistics: list[PeriodStatistics]


class MomentumGraphResponse(BaseModel):
    graphPoints: list[MomentumPoint]
    periodTime: int
    periodCount: int
    overtimeLength: int
