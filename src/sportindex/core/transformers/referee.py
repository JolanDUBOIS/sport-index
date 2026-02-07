from .common import transform_sport, transform_country


def transform_referee(raw: dict) -> dict:
    """ Transform raw referee data into a structured format. """
    return {
        "id": raw.get("id"),
        "slug": raw.get("slug"),
        "name": raw.get("name"),
        "games": raw.get("games"),
        "yellow_cards": raw.get("yellowCards"),
        "red_cards": raw.get("redCards"),
        "yellow_red_cards": raw.get("yellowRedCards"),
        "sport": transform_sport(raw.get("sport", {})),
        "country": transform_country(raw.get("country", {})),
    }
