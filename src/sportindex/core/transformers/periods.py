def transform_periods_descriptor(raw: dict) -> dict:
    """
    Example input:
    {
        "point": "Game",
        "current": "Match",
        "period1": "1st set",
        ...
    }
    """
    return {
        "units": {
            k: v for k, v in raw.items()
            if k in {"point", "current"}
        },
        "periods": {
            k: v for k, v in raw.items()
            if k.startswith("period")
        }
    }
