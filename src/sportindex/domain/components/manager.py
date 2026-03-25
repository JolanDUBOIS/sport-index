from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .common import Performance
    from ..competitor import Competitor
    from sportindex.provider.parsed import SofascoreProvider, ParsedManagerCareerHistoryItem


@dataclass(frozen=True)
class ManagerTenure:
    """Represents a manager's tenure at a club or national team."""
    performance: Performance | None
    team: Competitor
    start: datetime
    end: datetime

    @classmethod
    def _from_parsed(cls, parsed: ParsedManagerCareerHistoryItem | None, **kwargs) -> ManagerTenure | None:
        if parsed is None or parsed.team is None:
            return None
        from .common import Performance
        from ..competitor import Competitor
        provider: SofascoreProvider = kwargs.get("provider")
        return cls(
            performance=Performance._from_parsed(parsed.performance, **kwargs),
            team=Competitor(parsed.team, provider),
            start=parsed.start,
            end=parsed.end
        )
