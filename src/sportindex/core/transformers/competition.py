from .category import transform_category
from .common import transform_country
from .team import transform_team


def transform_season(raw: dict) -> dict:
    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "year": raw.get("year"),
    }

def transform_competition(raw: dict) -> dict:
    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "slug": raw.get("slug"),
        "gender": raw.get("gender"),
        "tier": raw.get("tier"),
        "category": transform_category(raw.get("category", {})),
        "country": transform_country(raw.get("country", {})),

        "lower_divisions": [transform_competition(comp) for comp in raw.get("lowerDivisions", [])],

        "title_holder": transform_team(raw.get("titleHolder", {})),
        "most_titles_teams": [transform_team(team) for team in raw.get("mostTitlesTeams", [])],

        "start_date_timestamp": raw.get("startDateTimestamp"), # Current season...
        "end_date_timestamp": raw.get("endDateTimestamp"), # Current season...
    }

def transform_tournament(raw: dict) -> dict:
    """
    Transform raw tournament data into a structured format.
    A tournament is a specific instance of a competition, often tied to a season or year.
    """
    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "slug": raw.get("slug"),
        "category": transform_category(raw.get("category", {})),
        "competition": transform_competition(raw.get("uniqueTournament", {})),
    }

# TODO - There is a link between season and tournament as a tournament is a specific instance of a competition, often tied to a season or year. 
# Try to find a way to link the two together in the data model...
