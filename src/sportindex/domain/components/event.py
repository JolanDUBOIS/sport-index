from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

from sportindex.provider.parsed import ParsedRound, ParsedMomentumPoint, ParsedStatisticsItem

if TYPE_CHECKING:
    from ..competitor import Competitor
    from sportindex.provider.parsed import (
        ParsedLineup, ParsedPeriod, ParsedScore,
        ParsedStatisticsGroup, ParsedPeriodStatistics
    )


# =====================================================================
# Match basic components
# =====================================================================

@dataclass(frozen=True)
class MatchCompetitors:
    """Represents the two competitors in a match."""
    home: Competitor
    away: Competitor


@dataclass(frozen=True)
class MatchScore:
    """Represents the score of a match."""
    home: int
    away: int

    @classmethod
    def _from_parsed(cls, parsed: ParsedScore | None) -> MatchScore | None:
        if parsed is None:
            return None
        return cls(**vars(parsed))


# =====================================================================
# Event Round
# =====================================================================

@dataclass(frozen=True)
class EventRound:
    """Represents the round or stage of a tournament that an event belongs to."""
    __annotations__ = ParsedRound.__annotations__

    @classmethod
    def _from_parsed(cls, parsed: ParsedRound | None, **kwargs) -> EventRound | None:
        if parsed is None:
            return None
        return cls(**vars(parsed))


# =====================================================================
# Lineups
# =====================================================================

@dataclass(frozen=True)
class TeamLineup:
    """Represents the lineup of a team for a match."""
    formation: str
    players: list[Competitor]
    missing_players: list[Competitor]

    @classmethod
    def _from_parsed(cls, parsed: ParsedLineup | None, **kwargs) -> TeamLineup | None:
        if parsed is None:
            return None
        provider = kwargs.get("provider")
        from ..competitor import Competitor
        return cls(
            formation=parsed.formation,
            players=[Competitor(p, provider) for p in parsed.players],
            missing_players=[Competitor(p, provider) for p in parsed.missingPlayers]
        )


@dataclass(frozen=True)
class MatchLineups:
    """Represents the lineups of both teams for a match."""
    home: list[TeamLineup]
    away: list[TeamLineup]


# =====================================================================
# Momentum Point
# =====================================================================

@dataclass(frozen=True)
class MatchMomentumPoint:
    """Represents a point in the match where momentum shifted, e.g. after a goal or key incident."""
    __annotations__ = ParsedMomentumPoint.__annotations__

    @classmethod
    def _from_parsed(cls, parsed: ParsedMomentumPoint | None, **kwargs) -> MatchMomentumPoint | None:
        if parsed is None:
            return None
        return cls(**vars(parsed))


# =====================================================================
# Match Periods
# =====================================================================

@dataclass(frozen=True)
class MatchPeriod:
    """Represents a period of a match."""
    key: str                                # e.g. "period1", "overtime", "penalties", "period2TieBreak"
    type: str                               # "normal", "overtime", "tiebreak", "penalties"
    label: str                              # Display label, e.g. "1st Half", "Overtime"
    score: MatchScore
    time: int                               # Actual elapsed time for this period (if known)
    defaultTime: int
    extraTime: list[int]                    # Injury/stoppage time added in this period

    @classmethod
    def _from_parsed(cls, parsed: ParsedPeriod | None) -> MatchPeriod | None:
        if parsed is None:
            return None
        return cls(
            key=parsed.key,
            type=parsed.type,
            label=parsed.label,
            score=MatchScore._from_parsed(parsed.score),
            time=parsed.time,
            defaultTime=parsed.defaultTime,
            extraTime=parsed.extraTime
        )


# =====================================================================
# Event Statistics
# =====================================================================

@dataclass(frozen=True)
class StatEntry:
    """Represents a single statistical item for a team in a match, e.g. possession percentage, shots on target, etc."""
    __annotations__ = ParsedStatisticsItem.__annotations__

    @classmethod
    def _from_parsed(cls, parsed: ParsedStatisticsItem | None) -> StatEntry | None:
        if parsed is None:
            return None
        return cls(**vars(parsed))


@dataclass(frozen=True)
class StatGroup:
    """Represents a group of statistical items for a team in a match."""
    name: str
    items: list[StatEntry]

    @classmethod
    def _from_parsed(cls, parsed: ParsedStatisticsGroup | None) -> StatGroup | None:
        if parsed is None:
            return None
        return cls(
            name=parsed.name,
            items=[StatEntry._from_parsed(i) for i in parsed.items]
        )


@dataclass(frozen=True)
class PeriodStats:
    """Represents the statistics for a team in a specific period of a match."""
    period: str
    groups: list[StatGroup]

    @classmethod
    def _from_parsed(cls, parsed: ParsedPeriodStatistics | None) -> PeriodStats | None:
        if parsed is None:
            return None
        return cls(
            period=parsed.period,
            groups=[StatGroup._from_parsed(g) for g in parsed.groups]
        )
