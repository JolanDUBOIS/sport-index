from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Cards:
    """Represents counts of disciplinary cards issued by a referee."""
    yellow: int
    red: int
    yellow_red: int
