from .player import transform_player


def transform_lineup(raw: dict) -> dict:
    """ Transform a single lineup entry for a detailed event. """
    return {
        "players": [transform_player(player) for player in raw.get("players", [])],
        "missing_players": [transform_player(player) for player in raw.get("missingPlayers", [])],
        "formation": raw.get("formation"),
    }

def transform_lineups(raw: dict) -> dict:
    """ Transform lineups information for a detailed event. """
    return {
        "home": transform_lineup(raw.get("home", {})),
        "away": transform_lineup(raw.get("away", {})),
    }
