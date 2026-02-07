# from .incident import transform_incident
# from ..event_old import transform_event
# from ..manager import transform_manager
# from ..player import transform_player


# def transform_lineup(raw: dict) -> dict:
#     """ Transform a single lineup entry for a detailed event. """
#     return {
#         "players": [transform_player(player) for player in raw.get("players", [])],
#         "missing_players": [transform_player(player) for player in raw.get("missingPlayers", [])],
#         "formation": raw.get("formation"),
#     }

# def transform_lineups(raw: dict) -> dict:
#     """ Transform lineups information for a detailed event. """
#     return {
#         "home": transform_lineup(raw.get("home", {})),
#         "away": transform_lineup(raw.get("away", {})),
#     }

# def transform_event_managers(raw: dict) -> dict:
#     """ Transform event managers information for a detailed event. """
#     return {
#         "home": transform_manager(raw.get("home", {})),
#         "away": transform_manager(raw.get("away", {})),
#     }

# def transform_detailed_event(raw: dict) -> dict:
#     """ Transform detailed event information. """
#     return {
#         "event": transform_event(raw.get("event", {})),
#         "incidents": [transform_incident(incident) for incident in raw.get("incidents", [])]
#     }
