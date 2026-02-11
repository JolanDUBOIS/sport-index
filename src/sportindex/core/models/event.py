from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal

from .core import BaseModel, Score, Status
from .period import Periods
from .referee import Referee
from .team import Team
from .tournament import Tournament, Season
from .utils import timestamp_to_iso
from .venue import Venue


@dataclass(frozen=True)
class Round(BaseModel):
    number: int
    name: Optional[str]
    slug: Optional[str]

    @classmethod
    def _from_api(cls, raw: dict) -> Round:
        return Round(
            number=raw.get("number"),
            name=raw.get("name"),
            slug=raw.get("slug"),
        )


@dataclass(frozen=True)
class EventDetails(BaseModel):
    outcome: Optional[Literal["home", "away", "draw"]] = None

    # Racket sports specific details
    first_to_serve: Optional[int] = None
    
    # Fight sports specific details
    type: Optional[str] = None
    order: Optional[list[int]] = None
    weight_class: Optional[str] = None
    win_type: Optional[str] = None
    final_round: Optional[int] = None

    @classmethod
    def _from_api(cls, raw: dict) -> EventDetails:
        if raw.get("winnerCode") == 1:
            outcome = "home"
        elif raw.get("winnerCode") == 2:
            outcome = "away"
        elif raw.get("winnerCode") == 3:
            outcome = "draw"
        else:
            outcome = None
        return EventDetails(
            outcome=outcome,
            first_to_serve=raw.get("firstToServe"),
            type=raw.get("fightType"),
            order=raw.get("order"),
            weight_class=raw.get("weightClass"),
            win_type=raw.get("winType"),
            final_round=raw.get("finalRound"),
        )
# NOTE - Separate this detail class into sub classes for different types of sports...


@dataclass(frozen=True)
class Event(BaseModel):
    id: str
    custom_id: str
    slug: str
    name: str
    start: str
    status: Status
    season: Season
    tournament: Tournament
    gender: Optional[str]
    participants: dict[str, Team]
    periods: Periods
    referee: Optional[Referee] = None
    score: Optional[Score] = None
    venue: Optional[Venue] = None
    attendance: Optional[int] = None
    round: Optional[Round] = None
    details: Optional[EventDetails] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Event:
        return Event(
            id=raw.get("id"),
            custom_id=raw.get("customId"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            start=timestamp_to_iso(raw.get("startTimestamp")),
            status=Status.from_api(raw.get("status")),
            season=Season.from_api(raw.get("season")),
            tournament=Tournament.from_api(raw.get("tournament")),
            gender=raw.get("gender"),
            participants={
                "home": Team.from_api(raw.get("homeTeam")),
                "away": Team.from_api(raw.get("awayTeam")),
            },
            periods=Periods.from_api(raw),
            referee=Referee.from_api(raw.get("referee")),
            score=Score(
                home=raw.get("homeScore", {}).get("display"),
                away=raw.get("awayScore", {}).get("display"),
            ) if "homeScore" in raw and "awayScore" in raw else None,
            venue=Venue.from_api(raw.get("venue")),
            attendance=raw.get("attendance"),
            round=Round.from_api(raw.get("roundInfo")),
            details=...,
        )
