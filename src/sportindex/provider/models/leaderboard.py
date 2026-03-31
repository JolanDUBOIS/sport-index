from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import Field

from .base import BaseSchema

if TYPE_CHECKING:
    from .core import _SportData, _CountryData, _CategoryData
    from .event import _EventData
    from .primitives import Promotion
    from .team import _TeamData
    from .tournament import _TournamentData, _UniqueTournamentData


# =====================================================================
# Team Standings
# =====================================================================

class _TeamStandingsEntryData(BaseSchema):
    id: int
    position: int
    matches: int | None = None
    wins: int | None = None
    draws: int | None = None
    losses: int | None = None
    points: float | None = None
    percentage: float | None = None          # Win percentage
    scores_for: int | None = None
    scores_against: int | None = None
    score_diff_formatted: str | None = None    # e.g. "+15"
    promotion: Promotion | None = None
    games_behind: float | None = None
    streak: int | None = None
    team: _TeamData | None = None


class _TeamStandingsData(BaseSchema):
    id: int
    name: str                  # e.g. "Premier League"
    type_: str = Field(default="total", alias="type")                  # "home", "away", "total"
    rows: list[_TeamStandingsEntryData] = Field(default_factory=list)
    tournament: _TournamentData | None = None
    updated_at: datetime | None = Field(default=None, alias="updatedAtTimestamp")


# =====================================================================
# Racing Standings
# =====================================================================

class _RacingStandingsEntryData(BaseSchema):
    start_number: int | None = None           # Driver or cyclist number
    number: int | None = None                 # alternative numbering, if API provides
    team: _TeamData | None = None
    parent_team: _TeamData | None = None
    updated_at: datetime | None = Field(default=None, alias="updatedAtTimestamp")

    # Position / Result
    position: int | None = None
    points: float | None = None
    interval: str | None = None               # Interval to competitor ahead
    gap: str | None = None                    # Gap to leader
    total_time: str | None = None
    time: str | None = None

    # Race-specific stats (Motorsport)
    grid_position: int | None = None
    laps: int | None = None
    laps_led: int | None = None
    victories: int | None = None
    races_started: int | None = None
    races_with_points: int | None = None
    pole_positions: int | None = None
    podiums: int | None = None
    fastest_laps: int | None = None
    fastest_lap_time: str | None = None
    personal_fastest_lap: int | None = None   # Which lap was driver's personal fastest
    personal_fastest_lap_time: str | None = None
    pit_stops: int | None = None
    tyre_type: str | None = None
    tyre_state: str | None = None

    # Cycling-specific
    sprint: int | None = None
    climb: int | None = None
    sprint_position: int | None = None
    climb_position: int | None = None
    shirt: str | None = None


# =====================================================================
# Rankings
# =====================================================================

class _RankingTypeData(BaseSchema):
    id: int
    slug: str
    name: str
    gender: str | None = None
    sport: _SportData | None = None
    category: _CategoryData | None = None
    unique_tournament: _UniqueTournamentData | None = None
    last_updated: datetime | None = None


class _RankingEntryData(BaseSchema):
    id: int
    name: str
    position: int         # For MMA, position starts at 0 instead of 1
    points: float | None = None
    team: _TeamData | None = None
    country: _CountryData | None = None

    best_position: int | None = None
    previous_position: int | None = None
    previous_points: float | None = None

    tournaments_played: int | None = None
    last_event: _EventData | None = None

    unique_tournament: _UniqueTournamentData | None = None
    playing_teams: int | None = None
    total_teams: int | None = None

    updated_at: datetime | None = Field(default=None, alias="updatedAtTimestamp")
