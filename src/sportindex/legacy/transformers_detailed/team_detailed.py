# from ..category import transform_category
# from ..common import transform_country
# from ..competition import transform_competition
# from ..manager import transform_manager
# from ..player import transform_player
# from ..team import transform_team
# from ..transfer import transform_transfer
# from ..venue import transform_venue
# from sportindex.utils import get_nested


# def transform_detailed_team(raw: dict) -> dict:
#     return {
#         "team": transform_team(raw.get("teamDetails", {})),
#         "category": transform_category(get_nested(raw, "teamDetails.category", {})),
#         "manager": transform_manager(get_nested(raw, "teamDetails.manager", {})),
#         "venue": transform_venue(get_nested(raw, "teamDetails.venue", {})),
#         "country": transform_country(get_nested(raw, "teamDetails.country", {})),
#         "history": {
#             "founded_timestamp": get_nested(raw, "teamDetails.foundationDateTimestamp"),
#             "achievements": {
#                 "total_trophies": get_nested(raw, "teamAchievements.totalTrophies"),
#                 "titles": [
#                     {
#                         "competition": transform_competition(get_nested(title, "uniqueTournament")),
#                         "count": title.get("count"),
#                     } for title in get_nested(raw, "teamAchievements.achievements", [])
#                 ]
#             }
#         },
#         "players": {
#             "all": [transform_player(player.get("player")) for player in get_nested(raw, "players.players", [])],
#             "foreign": [transform_player(player.get("player")) for player in get_nested(raw, "players.foreignPlayers", [])],
#             "national": [transform_player(player.get("player")) for player in get_nested(raw, "players.nationalPlayers", [])],
#             "previous-teams": [
#                 {
#                     "player": transform_player(player.get("player")),
#                     "previous_team": transform_team(get_nested(player, "previousTeam")),
#                     "transfer_date": player.get("transferDate"),
#                 }
#             for player in get_nested(raw, "players.previousTeams", [])
#             ],
#             "transfers": {
#                 "in": [transform_transfer(transfer) for transfer in get_nested(raw, "teamTransfers.transfersIn", [])],
#                 "out": [transform_transfer(transfer) for transfer in get_nested(raw, "teamTransfers.transfersOut", [])],
#             }
#         },
#         # We skip "featured event" as it doesn't seem relevant in the context of our client package
#         "competitions": [transform_competition(comp) for comp in get_nested(raw, "teamUniqueTournaments.uniqueTournaments", [])],
#     }