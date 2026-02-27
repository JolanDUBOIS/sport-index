def strip_unknown_keys(data: dict, td_type: type) -> dict:
    allowed = td_type.__annotations__.keys()
    return {k: data[k] for k in allowed if k in data}
