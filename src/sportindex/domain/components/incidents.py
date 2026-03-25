from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING
from dataclasses import dataclass

from sportindex.exceptions import InsufficientDataError

if TYPE_CHECKING:
    from .event import MatchScore
    from ..competitor import Competitor
    from ..manager import Manager
    from sportindex.provider.parsed import (
        ParsedIncident, ParsedGoalIncident, ParsedPenaltyIncident,
        ParsedPenaltyShootoutIncident, ParsedCardIncident, ParsedPeriodIncident,
        ParsedVarDecisionIncident, ParsedSubstitutionIncident, ParsedExtraTimeIncident
    )


# =====================================================================
# Incidents
# =====================================================================

class IncidentType(Enum):
    """Represents the type of an incident during a match."""
    GOAL = "goal"
    PENALTY = "penalty"
    PENALTY_SHOOTOUT = "penalty_shootout"
    CARD = "card"
    PERIOD = "period"
    VAR_DECISION = "var_decision"
    SUBSTITUTION = "substitution"
    EXTRA_TIME = "extra_time"


@dataclass(frozen=True)
class Incident:
    """Represents a significant event during a match, such as a goal, card, substitution, etc."""
    type_: IncidentType

    @classmethod
    def _from_parsed(cls, parsed: ParsedIncident | None, **kwargs) -> Incident | None:
        """Factory that converts parsed incident objects into domain incidents."""
        if parsed is None:
            return None
        itype = getattr(parsed, "incidentType", None)
        provider = kwargs.get("provider")

        _MAP: dict[str, type[Incident]] = {
            "goal": GoalIncident,
            "penalty": PenaltyIncident,
            "penaltyShootout": PenaltyShootoutIncident,
            "card": CardIncident,
            "period": PeriodIncident,
            "varDecision": VarDecisionIncident,
            "substitution": SubstitutionIncident,
            "injuryTime": ExtraTimeIncident,
        }

        handler = _MAP.get(itype)
        if handler is None:
            return None
        return handler._from_parsed(parsed, provider=provider)


@dataclass(frozen=True)
class GoalIncident(Incident):
    """Represents a goal scored during a match."""
    id: int
    time: int
    side: str                  # "home" / "away"
    score: MatchScore
    scorer: Competitor
    assist: Competitor
    extraTime: int             # stoppage-time minute offset
    kind: str                  # "regular", "ownGoal", "penalty" (football); "try", "twoPoints"... (rugby)

    @classmethod
    def _from_parsed(cls, parsed: ParsedGoalIncident | None, **kwargs) -> GoalIncident | None:
        if parsed is None:
            return None
        provider = kwargs.get("provider")
        from ..competitor import Competitor
        return cls(
            type_=IncidentType.GOAL,
            id=parsed.id,
            time=parsed.time,
            side=parsed.side,
            score=MatchScore._from_parsed(parsed.score),
            scorer=Competitor(parsed.scorer, provider=provider),
            assist=Competitor(parsed.assist, provider=provider),
            extraTime=parsed.extraTime,
            kind=parsed.kind
        )


@dataclass(frozen=True)
class PenaltyIncident(Incident):
    """Represents a penalty awarded during a match."""
    id: int
    time: int
    side: str
    shooter: Competitor
    extraTime: int
    description: str
    kind: str

    @classmethod
    def _from_parsed(cls, parsed: ParsedPenaltyIncident | None, **kwargs) -> PenaltyIncident | None:
        if parsed is None:
            return None
        provider = kwargs.get("provider")
        from ..competitor import Competitor
        return cls(
            type_=IncidentType.PENALTY,
            id=parsed.id,
            time=parsed.time,
            side=parsed.side,
            shooter=Competitor(parsed.shooter, provider=provider),
            extraTime=parsed.extraTime,
            description=parsed.description,
            kind=parsed.kind,
        )


@dataclass(frozen=True)
class PenaltyShootoutIncident(Incident):
    """Represents a penalty shootout attempt during a match."""
    id: int
    side: str
    score: MatchScore
    shooter: Competitor
    kind: str

    @classmethod
    def _from_parsed(cls, parsed: ParsedPenaltyShootoutIncident | None, **kwargs) -> PenaltyShootoutIncident | None:
        if parsed is None:
            return None
        provider = kwargs.get("provider")
        from ..competitor import Competitor
        return cls(
            type_=IncidentType.PENALTY_SHOOTOUT,
            id=parsed.id,
            side=parsed.side,
            score=MatchScore._from_parsed(parsed.score),
            shooter=Competitor(parsed.shooter, provider=provider),
            kind=parsed.kind,
        )


@dataclass(frozen=True)
class CardIncident(Incident):
    """Represents a disciplinary card issued during a match (e.g. yellow/red card in football)."""
    id: int
    time: int
    side: str
    recipient: Competitor | Manager
    rescinded: bool
    reason: str
    extraTime: int
    kind: str

    @classmethod
    def _from_parsed(cls, parsed: ParsedCardIncident | None, **kwargs) -> CardIncident | None:
        if parsed is None:
            return None
        provider = kwargs.get("provider")

        from ..competitor import Competitor
        from ..manager import Manager
        from sportindex.provider.parsed import ParsedPlayer, ParsedManager

        if isinstance(parsed.recipient, ParsedPlayer):
            recipient = Competitor(parsed.recipient, provider=provider)
        elif isinstance(parsed.recipient, ParsedManager):
            recipient = Manager(parsed.recipient, provider=provider)
        else:
            raise InsufficientDataError(f"Unknown card recipient type: {type(parsed.recipient)}")

        return cls(
            type_=IncidentType.CARD,
            id=parsed.id,
            time=parsed.time,
            side=parsed.side,
            recipient=recipient,
            rescinded=parsed.rescinded,
            reason=parsed.reason,
            extraTime=parsed.extraTime,
            kind=parsed.kind,
        )


@dataclass(frozen=True)
class PeriodIncident(Incident):
    """Represents a significant event related to a match period, such as the end of a half, start of overtime, etc."""
    time: int
    score: MatchScore
    kind: str

    @classmethod
    def _from_parsed(cls, parsed: ParsedPeriodIncident | None, **kwargs) -> PeriodIncident | None:
        if parsed is None:
            return None
        return cls(
            type_=IncidentType.PERIOD,
            time=parsed.time,
            score=MatchScore._from_parsed(parsed.score),
            kind=parsed.kind,
        )


@dataclass(frozen=True)
class VarDecisionIncident(Incident):
    """Represents a VAR (Video Assistant Referee) decision during a match, such as a goal review, penalty review, etc."""
    id: int
    time: int
    side: str
    extraTime: int
    description: str
    kind: str
    confirmed: bool

    @classmethod
    def _from_parsed(cls, parsed: ParsedVarDecisionIncident | None, **kwargs) -> VarDecisionIncident | None:
        if parsed is None:
            return None
        return cls(
            type_=IncidentType.VAR_DECISION,
            id=parsed.id,
            time=parsed.time,
            side=parsed.side,
            extraTime=parsed.extraTime,
            description=parsed.description,
            kind=parsed.kind,
            confirmed=parsed.confirmed,
        )


@dataclass(frozen=True)
class SubstitutionIncident(Incident):
    """Represents a player substitution during a match."""
    id: int
    time: int
    side: str
    playerIn: Competitor
    playerOut: Competitor
    extraTime: int
    kind: str

    @classmethod
    def _from_parsed(cls, parsed: ParsedSubstitutionIncident | None, **kwargs) -> SubstitutionIncident | None:
        if parsed is None:
            return None
        provider = kwargs.get("provider")
        from ..competitor import Competitor
        return cls(
            type_=IncidentType.SUBSTITUTION,
            id=parsed.id,
            time=parsed.time,
            side=parsed.side,
            playerIn=Competitor(parsed.playerIn, provider=provider),
            playerOut=Competitor(parsed.playerOut, provider=provider),
            extraTime=parsed.extraTime,
            kind=parsed.kind,
        )


@dataclass(frozen=True)
class ExtraTimeIncident(Incident):
    """Represents the addition of extra time (injury/stoppage time) during a match period."""
    time: int
    addedTime: int

    @classmethod
    def _from_parsed(cls, parsed: ParsedExtraTimeIncident | None, **kwargs) -> ExtraTimeIncident | None:
        if parsed is None:
            return None
        return cls(
            type_=IncidentType.EXTRA_TIME,
            time=parsed.time,
            addedTime=parsed.addedTime,
        )
