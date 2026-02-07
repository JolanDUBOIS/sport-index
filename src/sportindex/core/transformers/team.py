from .category import transform_category
from .common import transform_sport, transform_country
from .competition import transform_competition, transform_tournament
from .manager import transform_manager
from .venue import transform_venue
from sportindex.utils import get_nested


def transform_record(raw: dict) -> dict:
    """ Transform a team's win/draw/loss record. """
    return raw

def transform_team(raw: dict) -> dict:
    """ Transform raw team data into a structured format. """
    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "slug": raw.get("slug"),
        "short_name": raw.get("shortName"),
        "full_name": raw.get("fullName"),
        "name_code": raw.get("nameCode"),
        "national": raw.get("national"),
        "gender": raw.get("gender"),
        "ranking": raw.get("ranking"),
        "form": get_nested(raw, "pregameForm.form"),
        "manager": transform_manager(raw.get("manager", {})),
        "records": transform_record(raw.get("records", {})),
        "foundation_date_timestamp": raw.get("foundationDateTimestamp"),
        "venue": transform_venue(raw.get("venue", {})),
        "competition": transform_competition(raw.get("primaryUniqueTournament", {})),
        "tournament": transform_tournament(raw.get("tournament", {})),
        "category": transform_category(raw.get("category", {})),
        "sport": transform_sport(raw.get("sport", {})),
        "country": transform_country(raw.get("country", {})),
    }
