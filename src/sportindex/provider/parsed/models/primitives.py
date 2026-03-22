from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import BaseParsedModel
if TYPE_CHECKING:
    from sportindex.provider.raw.models import Channel


@dataclass
class ParsedChannel(BaseParsedModel):
    id: int
    name: str

    @classmethod
    def _parse(cls, raw: Channel) -> ParsedChannel:
        return cls(**raw.values())
