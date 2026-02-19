from __future__ import annotations
from dataclasses import dataclass

from .common import Amount
from .core import BaseModel
from .participants import Player, Team
from .utils import timestamp_to_iso


@dataclass(frozen=True, kw_only=True)
class Transfer(BaseModel):
    id: str
    date: str
    player: Player
    frm: Team
    to: Team
    fee: Amount

    @classmethod
    def _from_api(cls, raw: dict) -> Transfer:
        return Transfer(
            id=raw.get("id"),
            date=timestamp_to_iso(raw.get("transferDateTimestamp")),
            player=Player.from_api(raw.get("player")),
            frm=Team.from_api(raw.get("transferFrom")),
            to=Team.from_api(raw.get("transferTo")),
            fee=Amount.from_api(raw.get("transferFeeRaw")),
        )
