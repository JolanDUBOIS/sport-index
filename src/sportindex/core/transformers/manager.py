from .common import transform_country, transform_sport
from .team import transform_team
from sportindex.utils import get_nested


def transform_manager(raw: dict) -> dict:
    """ Transform raw manager data into a structured format. """
    return {
        "id": raw.get("id"),
        "slug": raw.get("slug"),
        "name": raw.get("name"),
        "short_name": raw.get("shortName"),
        "date_of_birth_timestamp": get_nested(raw, "dateOfBirthTimestamp"),
        "former_player_id": raw.get("formerPlayerId"),
        "preferred_formation": raw.get("preferredFormation"),
        "team": transform_team(raw.get("team", {})),
        "teams": [transform_team(team) for team in raw.get("teams", [])],
        "sport": transform_sport(raw.get("sport", {})),
        "country": transform_country({**raw.get("country", {}), "alpha3": raw.get("nationality")}),
        "performance": {
            "total": get_nested(raw, "performance.total"),
            "wins": get_nested(raw, "performance.wins"),
            "draws": get_nested(raw, "performance.draws"),
            "losses": get_nested(raw, "performance.losses"),
            "goal_scored": get_nested(raw, "performance.goalsScored"),
            "goals_conceded": get_nested(raw, "performance.goalsConceded"),
            "total_points": get_nested(raw, "performance.totalPoints"),
        },
    }
