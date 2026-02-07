from .team import transform_team
from .common import transform_country, transform_amount
from sportindex.utils import get_nested


def transform_player(raw: dict) -> dict:
    """ Transform raw player data into a structured format. """
    return {
        "id": raw.get("id"),
        "slug": raw.get("slug"),
        "name": raw.get("name"),
        "short_name": raw.get("shortName"),
        "height": raw.get("height"),
        "gender": raw.get("gender"),
        "date_of_birth": raw.get("dateOfBirth"),
        "date_of_birth_timestamp": raw.get("dateOfBirthTimestamp"),
        "number": raw.get("shirtNumber"),
        "position": {
            "position": raw.get("position"),
            "detailed": get_nested(raw, "position.positionsDetailed"),
        },
        "preferred_foot": raw.get("preferredFoot"),
        "retired": raw.get("retired"),
        "team": transform_team(raw.get("team", {})),
        "country": transform_country(raw.get("country", {})),
        "proposed_market_value": transform_amount(get_nested(raw, "proposedMarketValueRaw", {})),
    }
