from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal

from .common import Status, Score
from .core import BaseModel
from .period import Periods
from .referee import Referee
from .team import Team
from .tournament import Tournament, Season
from .utils import timestamp_to_iso
from .venue import Venue


@dataclass(frozen=True, kw_only=True)
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


@dataclass(frozen=True, kw_only=True)
class EventDetails(BaseModel):
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
        return EventDetails(
            first_to_serve=raw.get("firstToServe"),
            type=raw.get("fightType"),
            order=raw.get("order"),
            weight_class=raw.get("weightClass"),
            win_type=raw.get("winType"),
            final_round=raw.get("finalRound"),
        )
# NOTE - Separate this detail class into sub classes for different types of sports...
# Those are EXTRAS (cf tournaments...)


@dataclass(frozen=True, kw_only=True)
class Event(BaseModel):
    id: str
    custom_id: str
    slug: str
    start: str
    status: Status
    round: Round
    season: Season
    tournament: Tournament
    participants: dict[str, Team]
    periods: Periods
    gender: Optional[str] = None
    referee: Optional[Referee] = None
    score: Optional[Score] = None
    venue: Optional[Venue] = None
    attendance: Optional[int] = None
    outcome: Optional[Literal["home", "away", "draw"]] = None
    details: Optional[EventDetails] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Event:
        outcome_mapping = {
            1: "home",
            2: "away",
            3: "draw"
        }
        return Event(
            id=raw.get("id"),
            custom_id=raw.get("customId"),
            slug=raw.get("slug"),
            start=timestamp_to_iso(raw.get("startTimestamp")),
            status=Status.from_api(raw.get("status")),
            round=Round.from_api(raw.get("roundInfo")),
            season=Season.from_api(raw.get("season")),
            tournament=Tournament.from_api(raw.get("tournament")),
            participants={
                "home": Team.from_api(raw.get("homeTeam")),
                "away": Team.from_api(raw.get("awayTeam")),
            },
            periods=Periods.from_api(raw),
            gender=raw.get("gender"),
            referee=Referee.from_api(raw.get("referee")),
            score=Score(
                home=raw.get("homeScore", {}).get("display"),
                away=raw.get("awayScore", {}).get("display"),
            ) if "homeScore" in raw and "awayScore" in raw else None,
            venue=Venue.from_api(raw.get("venue")),
            attendance=raw.get("attendance"),
            outcome=outcome_mapping.get(raw.get("winnerCode")),
            details=EventDetails.from_api(raw),
        )

@dataclass(frozen=True, kw_only=True)
class Events(BaseModel):
    events: list[Event]
    has_next_page: Optional[bool] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Events:
        return Events(
            events=[Event.from_api(event) for event in raw.get("events", [])],
            has_next_page=raw.get("hasNextPage"),
        )
