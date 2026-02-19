from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional, Literal, List

from . import logger
from .common import Status, Score
from .core import BaseModel
from .participants import Referee, Team, Player
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


# === Events ===

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


# === Lineups ===

@dataclass(frozen=True, kw_only=True)
class Lineup(BaseModel):
    players: List[Player]
    missing_players: Optional[List[Player]] = None
    formation: Optional[str] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Lineup:
        return Lineup(
            players=[Player.from_api(player) for player in raw.get("players", [])],
            missing_players=[Player.from_api(player) for player in raw.get("missingPlayers", [])],
            formation=raw.get("formation"),
        )

@dataclass(frozen=True, kw_only=True)
class Lineups(BaseModel):
    home: Lineup
    away: Lineup

    @classmethod
    def _from_api(cls, raw: dict) -> Lineups:
        return Lineups(
            home=Lineup.from_api(raw.get("home")),
            away=Lineup.from_api(raw.get("away")),
        )


# === Periods ===

@dataclass(frozen=True, kw_only=True)
class Period:
    key: str # Used in Scores
    type: Literal["normal", "overtime", "tiebreak", "penalties"] # Specific addition of this package, not present in API, more will be added if discovered
    label: Optional[str] = None
    score: Optional[Score] = None
    time: Optional[int] = None
    default_time: Optional[int] = None # In case of period with subperiods (e.g. football overtime), this is the default time for one subperiod
    extra_time: Optional[tuple[int, ...]] = None

@dataclass(frozen=True, kw_only=True)
class Periods(BaseModel):
    default_count: int
    periods: list[Period]

    @classmethod
    def _from_api(cls, raw: dict) -> Periods:
        _raw = dict(raw) 
        if "homeScore" not in _raw:
            _raw["homeScore"] = {}
        if "awayScore" not in _raw:
            _raw["awayScore"] = {}

        if "defaultPeriodCount" not in _raw:
            logger.warning(f"Event {_raw.get('id')} does not have defaultPeriodCount.")
            return None

        default_count = _raw.get("defaultPeriodCount")
        default_period_time = _raw.get("defaultPeriodLength")
        default_overtime_time = _raw.get("defaultOvertimeLength")

        periods = []
        # Basic periods
        for k in range(1, default_count + 1):
            key = f"period{k}"
            score = Score(
                home=_raw["homeScore"].get(key),
                away=_raw["awayScore"].get(key)
            ) if key in _raw["homeScore"] and key in _raw["awayScore"] else None
            extra_time = _raw.get("time", {}).get(f"injuryTime{k}")
            periods.append(Period(
                key=key,
                type="normal",
                label=_raw.get("periods", {}).get(key),
                score=score,
                time=_raw.get("time", {}).get(key),
                default_time=default_period_time,
                extra_time=(extra_time,) if extra_time else None
            ))

        # Tie break periods (e.g. tennis)
        for k in range(1, default_count + 1):
            key = f"period{k}TieBreak"
            if key in _raw["homeScore"] and key in _raw["awayScore"]:
                score = Score(
                    home=_raw["homeScore"].get(key),
                    away=_raw["awayScore"].get(key)
                )
                periods.append(Period(
                    key=key,
                    type="tiebreak",
                    label=_raw.get("periods", {}).get(key) or _raw.get("periods", {}).get(f"period{k}") + " Tie-Break",
                    score=score
                ))

        # Overtime periods
        if "overtime" in _raw["homeScore"] and "overtime" in _raw["awayScore"]:
            score = Score(
                home=_raw["homeScore"].get("overtime"),
                away=_raw["awayScore"].get("overtime")
            )
            extra_time = []
            for key, value in _raw.get("time", {}).items():
                if key.startswith("injuryTime"):
                    try:
                        idx = int(key.removeprefix("injuryTime"))
                    except ValueError:
                        continue
                    if idx > default_count:
                        extra_time.append(value)
            periods.append(Period(
                key="overtime",
                type="overtime",
                label=_raw.get("periods", {}).get("overtime") or "Overtime",
                score=score,
                default_time=default_overtime_time,
                extra_time=tuple(extra_time) if extra_time else None
            ))

        # Penalty shootouts
        if "penalties" in _raw["homeScore"] and "penalties" in _raw["awayScore"]:
            score = Score(
                home=_raw["homeScore"].get("penalties"),
                away=_raw["awayScore"].get("penalties")
            )
            periods.append(Period(
                key="penalties",
                type="penalties",
                label=_raw.get("periods", {}).get("penalties") or "Penalty Shootout",
                score=score
            ))

        return Periods(
            default_count=default_count,
            periods=periods
        )


# === Event Statistics ===

@dataclass(frozen=True, kw_only=True)
class StatisticsItem(BaseModel):
    key: str
    name: str
    home: str
    away: str
    winner: Literal["home", "away", "tied"]
    polarity: Literal["positive", "negative"]

    @classmethod
    def _from_api(cls, raw: dict) -> StatisticsItem:
        winner_mapping = {
            1: "home",
            2: "away",
            3: "tied",
        }
        return StatisticsItem(
            key=raw.get("key"),
            name=raw.get("name"),
            home=raw.get("home"),
            away=raw.get("away"),
            winner=winner_mapping.get(raw.get("compareCode"), "tied"),
            polarity=raw.get("statisticsType", "positive"),
        )


@dataclass(frozen=True, kw_only=True)
class StatisticsGroup(BaseModel):
    name: str
    items: list[StatisticsItem]

    @classmethod
    def _from_api(cls, raw: dict) -> StatisticsGroup:
        return StatisticsGroup(
            name=raw.get("groupName"),
            items=[StatisticsItem.from_api(item) for item in raw.get("statisticsItems", [])],
        )


@dataclass(frozen=True, kw_only=True)
class PeriodStatistics(BaseModel):
    period: str
    groups: list[StatisticsGroup]

    @classmethod
    def _from_api(cls, raw: dict) -> PeriodStatistics:
        return PeriodStatistics(
            period=raw.get("period"),
            groups=[StatisticsGroup.from_api(group) for group in raw.get("groups", [])],
        )


@dataclass(frozen=True, kw_only=True)
class EventStatistics(BaseModel):
    periods: list[PeriodStatistics]

    @classmethod
    def _from_api(cls, raw: dict) -> EventStatistics:
        return EventStatistics(
            periods=[PeriodStatistics.from_api(period) for period in raw.get("statistics", [])],
        )


# === Momentum Graph ===

@dataclass(frozen=True, kw_only=True)
class MomentumPoint:
    minute: float
    value: int  # positive = home, negative = away, range ~[-100, 100]


@dataclass(frozen=True, kw_only=True)
class MomentumGraph(BaseModel):
    points: list[MomentumPoint]
    period_time: int
    period_count: int
    overtime_length: Optional[int] = None

    @classmethod
    def _from_api(cls, raw: dict) -> MomentumGraph:
        return MomentumGraph(
            points=[
                MomentumPoint(minute=p.get("minute"), value=p.get("value"))
                for p in raw.get("graphPoints", [])
            ],
            period_time=raw.get("periodTime"),
            period_count=raw.get("periodCount"),
            overtime_length=raw.get("overtimeLength"),
        )
