from .common import transform_sport, transform_country


def transform_transfer_period(raw: dict) -> dict:
    """ Transform raw transfer period data into a structured format. """
    return {
        "from": raw.get("activeFrom"),
        "to": raw.get("activeTo"),
    }

def transform_category(raw: dict) -> dict:
    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "slug": raw.get("slug"),
        "sport": transform_sport(raw.get("sport", {})),
        "country": transform_country(raw.get("country", {})),
        "transfer_periods": [transform_transfer_period(tp) for tp in raw.get("transferPeriod", [])],
    }
