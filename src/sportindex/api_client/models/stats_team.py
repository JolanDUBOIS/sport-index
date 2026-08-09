from __future__ import annotations

from .base import BaseSchema

# =====================================================================
# Team Season Stats
# =====================================================================

class TeamSeasonStats(BaseSchema):
    id: int | None = None
    goals_scored: int | None = None
    goals_conceded: int | None = None
    own_goals: int | None = None
    assists: int | None = None
    shots: int | None = None
    penalty_goals: int | None = None
    penalties_taken: int | None = None
    free_kick_goals: int | None = None
    free_kick_shots: int | None = None
    goals_from_inside_the_box: int | None = None
    goals_from_outside_the_box: int | None = None
    shots_from_inside_the_box: int | None = None
    shots_from_outside_the_box: int | None = None
    headed_goals: int | None = None
    left_foot_goals: int | None = None
    right_foot_goals: int | None = None
    big_chances: int | None = None
    big_chances_created: int | None = None
    big_chances_missed: int | None = None
    shots_on_target: int | None = None
    shots_off_target: int | None = None
    blocked_scoring_attempt: int | None = None
    successful_dribbles: int | None = None
    dribble_attempts: int | None = None
    corners: int | None = None
    hit_woodwork: int | None = None
    fast_breaks: int | None = None
    fast_break_goals: int | None = None
    fast_break_shots: int | None = None
    average_ball_possession: float | None = None
    total_passes: int | None = None
    accurate_passes: int | None = None
    accurate_passes_percentage: float | None = None
    total_own_half_passes: int | None = None
    accurate_own_half_passes: int | None = None
    accurate_own_half_passes_percentage: float | None = None
    total_opposition_half_passes: int | None = None
    accurate_opposition_half_passes: int | None = None
    accurate_opposition_half_passes_percentage: float | None = None
    total_long_balls: int | None = None
    accurate_long_balls: int | None = None
    accurate_long_balls_percentage: float | None = None
    total_crosses: int | None = None
    accurate_crosses: int | None = None
    accurate_crosses_percentage: float | None = None
    clean_sheets: int | None = None
    tackles: int | None = None
    interceptions: int | None = None
    saves: int | None = None
    errors_leading_to_goal: int | None = None
    errors_leading_to_shot: int | None = None
    penalties_commited: int | None = None
    penalty_goals_conceded: int | None = None
    clearances: int | None = None
    clearances_off_line: int | None = None
    last_man_tackles: int | None = None
    total_duels: int | None = None
    duels_won: int | None = None
    duels_won_percentage: float | None = None
    total_ground_duels: int | None = None
    ground_duels_won: int | None = None
    ground_duels_won_percentage: float | None = None
    total_aerial_duels: int | None = None
    aerial_duels_won: int | None = None
    aerial_duels_won_percentage: float | None = None
    possession_lost: int | None = None
    offsides: int | None = None
    fouls: int | None = None
    yellow_cards: int | None = None
    yellow_red_cards: int | None = None
    red_cards: int | None = None
    avg_rating: float | None = None
    accurate_final_third_passes_against: int | None = None
    accurate_opposition_half_passes_against: int | None = None
    accurate_own_half_passes_against: int | None = None
    accurate_passes_against: int | None = None
    big_chances_against: int | None = None
    big_chances_created_against: int | None = None
    big_chances_missed_against: int | None = None
    clearances_against: int | None = None
    corners_against: int | None = None
    crosses_successful_against: int | None = None
    crosses_total_against: int | None = None
    dribble_attempts_total_against: int | None = None
    dribble_attempts_won_against: int | None = None
    errors_leading_to_goal_against: int | None = None
    errors_leading_to_shot_against: int | None = None
    hit_woodwork_against: int | None = None
    interceptions_against: int | None = None
    key_passes_against: int | None = None
    long_balls_successful_against: int | None = None
    long_balls_total_against: int | None = None
    offsides_against: int | None = None
    red_cards_against: int | None = None
    shots_against: int | None = None
    shots_blocked_against: int | None = None
    shots_from_inside_the_box_against: int | None = None
    shots_from_outside_the_box_against: int | None = None
    shots_off_target_against: int | None = None
    shots_on_target_against: int | None = None
    blocked_scoring_attempt_against: int | None = None
    tackles_against: int | None = None
    total_final_third_passes_against: int | None = None
    opposition_half_passes_total_against: int | None = None
    own_half_passes_total_against: int | None = None
    total_passes_against: int | None = None
    yellow_cards_against: int | None = None
    throw_ins: int | None = None
    goal_kicks: int | None = None
    ball_recovery: int | None = None
    free_kicks: int | None = None
    kilometers_covered: float | None = None
    number_of_sprints: int | None = None
    matches: int | None = None
    awarded_matches: int | None = None


# =====================================================================
# Team Year Stats (Tennis)
# =====================================================================

class TeamYearSurfaceStats(BaseSchema):
    matches: int | None = None
    ground_type: str | None = None        # e.g. "Hardcourt indoor", "Red clay", "Grass"
    total_serve_attempts: int | None = None
    tiebreak_losses: int | None = None
    tiebreaks_won: int | None = None
    tournaments_won: int | None = None
    tournaments_played: int | None = None
    wins: int | None = None
    aces: int | None = None
    first_serve_points_scored: int | None = None
    first_serve_points_total: int | None = None
    first_serve_total: int | None = None
    second_serve_points_scored: int | None = None
    second_serve_points_total: int | None = None
    second_serve_total: int | None = None
    break_points_scored: int | None = None
    break_points_total: int | None = None
    opponent_break_points_total: int | None = None
    opponent_break_points_scored: int | None = None
    winners_total: int | None = None
    unforced_errors_total: int | None = None
    double_faults: int | None = None
