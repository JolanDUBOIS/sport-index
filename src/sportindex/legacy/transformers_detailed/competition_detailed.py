# from ..competition import transform_competition, transform_season
# from ..team import transform_team
# from sportindex.utils import get_nested


# def transform_detailed_competition(raw: dict) -> dict:

#     def _transform_tv_partner(raw: dict) -> dict:
#         return raw

#     def _transform_organisation(raw: dict) -> dict:
#         return raw

#     def _transform_promotion(raw: dict) -> dict:
#         return {"competition_name": raw.get("competitionName"), "promotion_count": raw.get("promotionCount")}

#     return {
#         "competition": transform_competition(raw.get("uniqueTournament", {})),
#         "seasons": {
#             "current": transform_season(get_nested(raw, "info.season", {})),
#             "all": [transform_season(season) for season in raw.get("seasons", [])],
#             "meta": {
#                 "first_season_year": get_nested(raw, "seo.firstSeasonYear"),
#             }
#         },
#         "classification": {
#             "type": get_nested(raw, "seo.competitionType"),
#             "gender": get_nested(raw, "seo.gender"),
#             "grade": get_nested(raw, "seo.grade"),
#             "organisation": _transform_organisation(get_nested(raw, "seo.officialOrganisation", {})),
#         },
#         "season_transition": {
#             "promotions": [
#                 _transform_promotion(promo)
#                 for promo in get_nested(raw, "seo.promotions", [])
#             ],
#             "has_playoffs": get_nested(raw, "seo.hasPlayoffs"),

#             "new_comers_upper_division": [
#                 transform_team(team) for team in get_nested(raw, "info.newcomersUpperDivision", [])
#             ],
#             "new_comers_lower_division": [
#                 transform_team(team) for team in get_nested(raw, "info.newcomersLowerDivision", [])
#             ],
#             "new_comers_other": [
#                 transform_team(team) for team in get_nested(raw, "info.newcomersOther", [])
#             ],
#             "number_of_competitors": get_nested(raw, "info.numberOfCompetitors"),
#         },
#         "statistics": {
#             "largest_stadium": {
#                 "team_name": get_nested(raw, "seo.largestStadium.teamName"),
#                 "capacity": get_nested(raw, "seo.largestStadium.capacity"),
#             },
#             "last_season_attendance": {
#                 "total": get_nested(raw, "seo.lastSeasonAttendance.total"),
#                 "average": get_nested(raw, "seo.lastSeasonAttendance.average"),
#                 "highest": get_nested(raw, "seo.lastSeasonAttendance.highest"),
#                 "highest_home_team": get_nested(raw, "seo.lastSeasonAttendance.highestHomeTeam"),
#                 "highest_away_team": get_nested(raw, "seo.lastSeasonAttendance.highestAwayTeam"),
#             },
#             "matches": {
#                 "home_team_wins": get_nested(raw, "info.homeTeamWins"),
#                 "away_team_wins": get_nested(raw, "info.awayTeamWins"),
#                 "draws": get_nested(raw, "info.draws"),
#             },
#             "goals": get_nested(raw, "info.goals"),
#             "discipline": {
#                 "yellow_cards": get_nested(raw, "info.yellowCards"),
#                 "red_cards": get_nested(raw, "info.redCards"),
#             },
#         },
#         "history": {
#             "first_season_winner": get_nested(raw, "seo.firstSeasonWinner"),
#             "most_titles_teams": [transform_team(team) for team in get_nested(raw, "uniqueTournament.mostTitlesTeams", [])],
#         },
#         "media": {
#             "other_names": get_nested(raw, "seo.otherNames", []),
#             "tv_partners": [_transform_tv_partner(partner) for partner in get_nested(raw, "seo.tvPartners", [])],
#         },
#     }