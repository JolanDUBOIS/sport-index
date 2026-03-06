from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..base import BaseParsedModel
if TYPE_CHECKING:
    from ..player import ParsedPlayer
    from sportindex.core.provider.models import Lineup


# =====================================================================
# Lineups
# =====================================================================

@dataclass
class ParsedLineup(BaseParsedModel):
    formation: str
    players: list[ParsedPlayer]
    missingPlayers: list[ParsedPlayer]

    @classmethod
    def _parse(cls, raw: Lineup) -> ParsedLineup:
        from ..player import ParsedPlayer
        return cls(
            formation=raw.get("formation"),
            players=[ParsedPlayer.from_raw(p) for p in raw.get("players", [])],
            missingPlayers=[ParsedPlayer.from_raw(p) for p in raw.get("missingPlayers", [])]
        )
