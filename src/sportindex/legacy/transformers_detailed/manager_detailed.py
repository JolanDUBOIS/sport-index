# from ..manager import transform_manager
# from ..team import transform_team
# from sportindex.utils import get_nested


# def transform_detailed_manager(raw: dict) -> dict:
#     return {
#         "manager": transform_manager(get_nested(raw, "managerDetails.manager", {})),
#         "performance": {
#             "total": get_nested(raw, "managerDetails.performance.total"),
#             "wins": get_nested(raw, "managerDetails.performance.wins"),
#             "draws": get_nested(raw, "managerDetails.performance.draws"),
#             "losses": get_nested(raw, "managerDetails.performance.losses"),
#             "goal_scored": get_nested(raw, "managerDetails.performance.goalsScored"),
#             "goals_conceded": get_nested(raw, "managerDetails.performance.goalsConceded"),
#             "total_points": get_nested(raw, "managerDetails.performance.totalPoints"),
#         },
#         "history": {
#             "teams": [
#                 {
#                     "team": transform_team(get_nested(team, "team")),
#                     "from_timestamp": team.get("startTimestamp"),
#                     "to_timestamp": team.get("endTimestamp"),
#                 }
#                 for team in get_nested(raw, "managerCareerHistory.careerHistory", [])
#             ]
#         }
#     }
