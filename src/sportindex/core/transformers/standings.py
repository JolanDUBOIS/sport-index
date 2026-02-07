from .competition import transform_tournament
from .team import transform_team


def transform_standings_team_entry(raw: dict) -> dict:
    """ Transform a single team entry in the standings. """
    return {
        "id": raw.get("id"),
        "team": transform_team(raw.get("team", {})),
        "position": raw.get("position"),
        "points": raw.get("points"),
        "matches": raw.get("matches"),
        "wins": raw.get("wins"),
        "draws": raw.get("draws"),
        "losses": raw.get("losses"),
        "scores_for": raw.get("scoresFor"),
        "scores_against": raw.get("scoresAgainst"),
        "score_difference": raw.get("scoreDiffFormatted"),
    }

def transform_standings(raw: dict) -> dict:
    """ Transform raw standings data into a structured format. """
    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "tournament": transform_tournament(raw.get("tournament", {})),
        "standings": [transform_standings_team_entry(entry) for entry in raw.get("rows", [])]
    }
