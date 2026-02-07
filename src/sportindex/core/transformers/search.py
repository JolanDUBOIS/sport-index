from typing import Literal

from .competition import transform_competition
from .event import transform_event
from .manager import transform_manager
from .player import transform_player
from .referee import transform_referee
from .team import transform_team
from .venue import transform_venue


MAPPING = {
    "competitions": transform_competition,
    "teams": transform_team,
    "players": transform_player,
    "managers": transform_manager,
    "referees": transform_referee,
    "venues": transform_venue,
    "events": transform_event,
}

def transform_search_results(
    target: Literal["competitions", "teams", "players", "managers", "referees", "venues", "events"],
    raw: dict
) -> dict:
    """ Transform raw search results into a standardized format. """
    raw_results = raw.get("results", [])
    return {target: [MAPPING[target](item.get("entity")) for item in raw_results]}
