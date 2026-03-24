from __future__ import annotations

from typing import TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from ..manager import RawManager
    from ..player import RawPlayer


class RawIncident(TypedDict, total=False):
    incidentType: str
    id: int
    time: int
    side: str
    homeScore: int
    awayScore: int
    isHome: bool
    player: RawPlayer
    assist: RawPlayer
    manager: RawManager
    addedTime: int
    incidentClass: str
    description: str
    rescinded: bool
    reason: str
    text: str
    confirmed: bool
    playerIn: RawPlayer
    playerOut: RawPlayer
    length: int
