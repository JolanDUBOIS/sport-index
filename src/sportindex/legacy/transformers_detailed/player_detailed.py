# from ..player import transform_player
# from ..transfer import transform_transfer
# from ..competition import transform_competition
# from sportindex.utils import get_nested


# def transform_detailed_player(raw: dict) -> dict:
#     return {
#         "player": transform_player(raw.get("player", {})),
#         "transfers": [transform_transfer(transfer) for transfer in get_nested(raw, "transfers", [])],
#         "competitions": [transform_competition(comp) for comp in raw.get("uniqueTournamentsMap", {}).values()],
#     }