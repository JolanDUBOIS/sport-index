def transform_country(raw: dict) -> dict:
    """ Transform raw country data into a structured format. """
    return raw

def transform_city(raw: dict) -> dict:
    """ Transform raw city data into a structured format. """
    return raw

def transform_sport(raw: dict) -> dict:
    """ Transform raw sport data into a structured format. """
    return raw

def transform_amount(raw: dict) -> dict:
    """ Transform raw amount data (e.g., transfer fee, market value) into a structured format. """
    return {
        "value": raw.get("value"),
        "currency": raw.get("currency"),
    }
