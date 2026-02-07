from .common import transform_country, transform_city
from .team import transform_team
from sportindex.utils import get_nested


def transform_stadium(raw: dict) -> dict:
    """ Transform raw stadium data into a structured format. """
    return raw

def transform_venue(raw: dict) -> dict:
    """ Transform raw venue data into a structured format. """
    return {
        "id": raw.get("id"),
        "slug": raw.get("slug"),
        "name": raw.get("name"),
        "capacity": raw.get("capacity"),
        "coordinates": {
            "latitude": get_nested(raw, "venueCoordinates.latitude"),
            "longitude": get_nested(raw, "venueCoordinates.longitude"),
        },
        "country": transform_country(raw.get("country", {})),
        "city": transform_city(raw.get("city", {})),
        "stadium": transform_stadium(raw.get("stadium", {})), # Not sure how valuable this is, as it seems to be just the name of the stadium & the capacity, both already included...
        "main_teams": [transform_team(team) for team in raw.get("mainTeams", [])],
    }
