from .category import transform_category
from .common import transform_sport, transform_country
from .competition import transform_competition
from .event_old import transform_event
from .team import transform_team
from sportindex.utils import get_nested


def transform_ranking_entry(raw: dict) -> dict:
    """ Transform a single ranking entry. """
    return {
        "id": raw.get("id"),
        "position": raw.get("position"),
        "previous_position": raw.get("previousPosition"),
        "points": raw.get("points"),
        "previous_points": raw.get("previousPoints"),
        "updated_timestamp": raw.get("updatedTimestamp"),
        "country": transform_country(raw.get("country")),
        "team": transform_team(raw.get("team")),
        "last_event": transform_event(raw.get("lastEvent")),
    }

def transform_rankings(raw: dict) -> dict:
    """ Transform raw ranking data into a structured format. """
    return {
        "id": get_nested(raw, "rankingType.id"),
        "slug": get_nested(raw, "rankingType.slug"),
        "name": get_nested(raw, "rankingType.name"),
        "gender": get_nested(raw, "rankingType.gender"),
        "sport": transform_sport(get_nested(raw, "rankingType.sport")),
        "last_updated_timestamp": get_nested(raw, "rankingType.lastUpdatedTimestamp"),
        "category": transform_category(get_nested(raw, "rankingType.category")),
        "competition": transform_competition(get_nested(raw, "rankingType.uniqueTournament")),
        "rankings": [transform_ranking_entry(entry) for entry in raw.get("rankingRows", [])]
    }
