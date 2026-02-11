from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal

from . import logger
from .core import BaseModel, Score
from .manager import Manager
from .player import Player


@dataclass(frozen=True)
class Incident(BaseModel):
    @staticmethod
    def _get_side(raw: dict) -> Optional[Literal["home", "away"]]:
        if "isHome" not in raw:
            return None
        return "home" if raw.get("isHome") else "away"

    @staticmethod
    def _get_score(raw: dict) -> Optional[Score]:
        if "homeScore" in raw and "awayScore" in raw:
            return Score(home=raw.get("homeScore"), away=raw.get("awayScore"))
        return None

    @classmethod
    def _from_api(cls, raw: dict) -> Incident:
        incident_type = raw.get("incidentType")
        mapping: dict[str, type[Incident]] = {
            "goal": GoalIncident,
            "penalty": PenaltyIncident,
            "penaltyShootout": PenaltyShootoutIncident,
            "card": CardIncident,
            "period": PeriodIncident,
            "varDecision": VarDecisionIncident,
            "substitution": SubstitutionIncident,
            "injuryTime": ExtraTimeIncident,
        }
        incident_cls = mapping.get(incident_type)
        if not incident_cls:
            logger.warning(f"Unknown incident type '{incident_type}' encountered. Returning None for this incident.")
            return None
        return incident_cls.from_api(raw)

@dataclass(frozen=True)
class GoalIncident(Incident):
    id: str
    time: int
    scorer: Player
    side: Literal["home", "away"]
    extra_time: Optional[int] = None
    assist: Optional[Player] = None
    score: Optional[Score] = None
    kind: Optional[str] = None # e.g. "penalty", "ownGoal", "regular" for football, "try", "twoPoints", "threePoints"... for rugby, etc.
    # NOTE - Add passing network info

    @classmethod
    def _from_api(cls, raw: dict) -> GoalIncident:
        return GoalIncident(
            id=raw.get("id"),
            time=raw.get("time"),
            scorer=Player.from_api(raw.get("player")),
            side=cls._get_side(raw),
            extra_time=raw.get("addedTime"),
            assist=Player.from_api(raw.get("assist")),
            score=cls._get_score(raw),
            kind=raw.get("incidentClass"),
        )

@dataclass(frozen=True)
class PenaltyIncident(Incident): # If missed, because if scored, it's a goal incident
    id: str
    time: int
    shooter: Player
    side: Literal["home", "away"]
    extra_time: Optional[int] = None
    description: Optional[str] = None
    kind: Optional[str] = None # e.g. "missed" (idk what other options there might be...)
    # NOTE - Add passing network info

    @classmethod
    def _from_api(cls, raw: dict) -> PenaltyIncident:
        return PenaltyIncident(
            id=raw.get("id"),
            time=raw.get("time"),
            shooter=Player.from_api(raw.get("player")),
            side=cls._get_side(raw),
            extra_time=raw.get("addedTime"),
            description=raw.get("description"),
            kind=raw.get("incidentClass"),
        )

@dataclass(frozen=True)
class PenaltyShootoutIncident(Incident):
    id: str
    shooter: Player
    side: Literal["home", "away"]
    score: Optional[Score] = None
    kind: Optional[str] = None # e.g. "scored", "missed", etc.

    @classmethod
    def _from_api(cls, raw: dict) -> PenaltyShootoutIncident:
        return PenaltyShootoutIncident(
            id=raw.get("id"),
            shooter=Player.from_api(raw.get("player")),
            side=cls._get_side(raw),
            score=cls._get_score(raw),
            kind=raw.get("incidentClass"),
        )

@dataclass(frozen=True)
class CardIncident(Incident):
    id: str
    time: int # If time -5, it means the card was given on the bench...
    recipient: Player | Manager
    rescinded: bool
    side: Literal["home", "away"]
    reason: Optional[str] = None
    extra_time: Optional[int] = None
    kind: Optional[str] = None # e.g. "yellow", "red"...

    @classmethod
    def _from_api(cls, raw: dict) -> CardIncident:
        return CardIncident(
            id=raw.get("id"),
            time=raw.get("time"),
            recipient=Player.from_api(raw.get("player")) if raw.get("player") else Manager.from_api(raw.get("manager")),
            rescinded=raw.get("rescinded"),
            side=cls._get_side(raw),
            reason=raw.get("reason"),
            extra_time=raw.get("addedTime"),
            kind=raw.get("incidentClass"),
        )

@dataclass(frozen=True)
class PeriodIncident(Incident):
    time: Optional[int] = None # If 999, replace by None
    score: Optional[Score] = None
    kind: Optional[str] = None # e.g. "HT", "FT", "PEN", etc.

    @classmethod
    def _from_api(cls, raw: dict) -> PeriodIncident:
        return PeriodIncident(
            time=raw.get("time") if raw.get("time") != 999 else None,
            score=cls._get_score(raw),
            kind=raw.get("text"),
        )

@dataclass(frozen=True)
class ExtraTimeIncident(Incident):
    time: int
    added_time: int # Voluntarily use added_time instead of extra_time to avoid confusion with the time of the other incidents

    @classmethod
    def _from_api(cls, raw: dict) -> ExtraTimeIncident:
        return ExtraTimeIncident(
            time=raw.get("time"),
            added_time=raw.get("length"),
        )

@dataclass(frozen=True)
class VarDecisionIncident(Incident):
    id: str
    time: int
    side: Literal["home", "away"]
    extra_time: Optional[int] = None
    description: Optional[str] = None
    kind: Optional[str] = None # e.g. "goalAwarded", "penaltyCheck", etc.
    confirmed: Optional[bool] = None # e.g. for a goal awarded after a VAR check, whether the goal was confirmed or not after the check

    @classmethod
    def _from_api(cls, raw: dict) -> VarDecisionIncident:
        return VarDecisionIncident(
            id=raw.get("id"),
            time=raw.get("time"),
            side=cls._get_side(raw),
            extra_time=raw.get("addedTime"),
            description=raw.get("text"),
            kind=raw.get("incidentClass"),
            confirmed=raw.get("confirmed"),
        )

@dataclass(frozen=True)
class SubstitutionIncident(Incident):
    id: str
    time: int
    player_in: Player
    player_out: Player
    side: Literal["home", "away"]
    extra_time: Optional[int] = None
    kind: Optional[str] = None # e.g. "regular", "injury", etc.

    @classmethod
    def _from_api(cls, raw: dict) -> SubstitutionIncident:
        return SubstitutionIncident(
            id=raw.get("id"),
            time=raw.get("time"),
            player_in=Player.from_api(raw.get("playerIn")),
            player_out=Player.from_api(raw.get("playerOut")),
            side=cls._get_side(raw),
            extra_time=raw.get("addedTime"),
            kind=raw.get("incidentClass"),
        )
