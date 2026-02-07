from .common import transform_amount
from .player import transform_player
from .team import transform_team
from sportindex.utils import get_nested


def transform_transfer(raw: dict) -> dict:
    """ Transform raw transfer data into a structured format. """
    return {
        "id": raw.get("id"),
        "player": transform_player(raw.get("player", {})),
        "from_team": transform_team(get_nested(raw, "transferFrom")),
        "to_team": transform_team(get_nested(raw, "transferTo")),
        "fee": transform_amount(get_nested(raw, "transferFeeRaw", {})),
        "date_timestamp": raw.get("transferDateTimestamp"),
    }
