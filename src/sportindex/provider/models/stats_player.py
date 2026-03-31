from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import Field

from .base import BaseSchema

if TYPE_CHECKING:
    from .team import _TeamData
    from .tournament import _SeasonData, _UniqueTournamentData


class PlayerSeasonStatsItem(BaseSchema):
    id: int | None = None
    accurate_crosses: int | None = None
    accurate_crosses_percentage: float | None = None
    accurate_long_balls: int | None = None
    accurate_long_balls_percentage: float | None = None
    accurate_passes: int | None = None
    accurate_passes_percentage: float | None = None
    assists: int | None = None
    big_chances_created: int | None = None
    big_chances_missed: int | None = None
    blocked_shots: int | None = None
    clean_sheet: int | None = None
    dribbled_past: int | None = None
    error_lead_to_goal: int | None = None
    expected_assists: float | None = None
    expected_goals: float | None = None
    goals: int | None = None
    goals_assists_sum: int | None = None
    goals_conceded: int | None = None
    interceptions: int | None = None
    key_passes: int | None = None
    minutes_played: int | None = None
    pass_to_assist: int | None = None
    rating: float | None = None
    red_cards: int | None = None
    saves: int | None = None
    shots_on_target: int | None = None
    successful_dribbles: int | None = None
    tackles: int | None = None
    total_shots: int | None = None
    yellow_cards: int | None = None
    total_rating: float | None = None
    count_rating: int | None = None
    total_long_balls: int | None = None
    total_cross: int | None = None
    total_passes: int | None = None
    shots_from_inside_the_box: int | None = None
    appearances: int | None = None


class PlayerSeasonStats(BaseSchema):
    year: str | None = None
    start_year: int | None = None
    end_year: int | None = None
    statistics: PlayerSeasonStatsItem | None = None
    team: _TeamData | None = None
    unique_tournament: _UniqueTournamentData | None = None
    season: _SeasonData | None = None
