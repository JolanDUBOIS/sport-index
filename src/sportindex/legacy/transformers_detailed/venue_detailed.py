# from ..event_old import transform_event
# from ..venue import transform_venue
# from sportindex.utils import get_nested


# def transform_detailed_venue(raw: dict) -> dict:
#     """ Transform detailed venue information. """
#     return {
#         "venue": transform_venue(get_nested(raw, "venueDetails.venue", {})),
#         "statistics": {
#             "total_matches": get_nested(raw, "venueDetails.statistics.totalMatches"),
#             "home_team_goals": get_nested(raw, "venueDetails.statistics.homeTeamGoalsScored"),
#             "away_team_goals": get_nested(raw, "venueDetails.statistics.awayTeamGoalsScored"),
#             "avg_red_cards_per_game": get_nested(raw, "venueDetails.statistics.avgRedCardsPerGame"),
#             "avg_corner_kicks_per_game": get_nested(raw, "venueDetails.statistics.avgCornerKicksPerGame"),
#             "home_team_win_percentage": get_nested(raw, "venueDetails.statistics.homeTeamWinPercentage"),
#             "away_team_win_percentage": get_nested(raw, "venueDetails.statistics.awayTeamWinPercentage"),
#             "draw_percentage": get_nested(raw, "venueDetails.statistics.drawPercentage"),
#         },
#         "next_event": transform_event(raw.get("nextEvent", {})),
#     }
