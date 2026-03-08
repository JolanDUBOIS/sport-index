from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from ..manager import Manager
    from ..player import Player


class Incident(TypedDict, total=False):
    incidentType: str
    id: int
    time: int
    side: str
    homeScore: int
    awayScore: int
    isHome: bool
    player: Player
    assist: Player
    manager: Manager
    addedTime: int
    incidentClass: str
    description: str
    rescinded: bool
    reason: str
    text: str
    confirmed: bool
    playerIn: Player
    playerOut: Player
    length: int
