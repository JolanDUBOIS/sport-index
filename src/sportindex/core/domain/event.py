"""
Event domain entity.

An Event represents a single match, fight, race session, etc.

Match-specific data (home/away teams, results, details, incidents,
lineups, statistics, head-to-head, momentum) is accessed via
:attr:`Event.match` → :class:`MatchData`.

Race/stage-specific data (results, details) is accessed via
:attr:`Event.race` → :class:`RaceData`.

Exactly one of ``event.match`` and ``event.race`` is non-``None``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Literal, TYPE_CHECKING

from .base import BaseEntity
from .values import (
    Score,
    Status,
    Round,
    _status_from_raw,
    _score_from_raw,
    _round_from_raw,
)
from ..provider.parsers import (
    timestamp_to_dt,
    get_event_outcome,
    get_display_score,
    parse_periods,
    parse_incidents,
    ParsedPeriods,
    ParsedIncident,
)

if TYPE_CHECKING:
    from .competition import Competition
    from .leaderboard import StandingsEntry
    from .participant import Competitor, Referee
    from .season import Season
    from .venue import Venue

logger = logging.getLogger(__name__)


class Event(BaseEntity):
    """A single event (match, fight, race session, etc.).

    Exactly one of :attr:`match` and :attr:`race` is non-``None``:

    - ``event.match`` → :class:`MatchData` (home/away, results, incidents, …)
    - ``event.race``  → :class:`RaceData`  (results, details, …)
    """

    def __init__(
        self,
        *,
        id: int,
        slug: str,
        name: str = "",
        start: Optional[datetime] = None,
        status: Optional[Status] = None,
    ) -> None:
        super().__init__()
        self.id = id
        self.slug = slug
        self.name = name
        self.start = start
        self.status = status

        # Eagerly populated from raw if available
        self._round: Optional[Round] = None
        self._venue: Optional[Venue] = None
        self._season: Optional[Season] = None

        # Type-specific bundles (exactly one is non-None)
        self._match: Optional[MatchData] = None
        self._race: Optional[RaceData] = None

    # -- Constructor --------------------------------------------------- #

    @classmethod
    def _from_raw_event(cls, raw: dict) -> Event:
        """Build from a RawEvent dict."""
        ev = cls(
            id=raw.get("id", 0),
            slug=raw.get("slug", ""),
            name=raw.get("slug", ""),        # events never have "name" field
            start=timestamp_to_dt(raw.get("startTimestamp")),
            status=_status_from_raw(raw.get("status")),
        )
        ev._raw = raw
        ev._round = _round_from_raw(raw.get("roundInfo"))

        # Delegate match construction to MatchData
        ev._match = MatchData._from_raw(raw, ev)

        # Season + competition
        from .season import Season
        from .competition import Competition
        if "season" in raw and raw["season"]:
            raw_unique_tournament = raw.get("tournament", {}).get("uniqueTournament")
            if raw_unique_tournament:
                competition = Competition._from_raw_unique_tournament(raw_unique_tournament)
                ev._season = Season._from_raw_season_tournament(
                    raw["season"],
                    competition=competition,
                )

        return ev

    @classmethod
    def _from_raw_stage(cls, raw: dict) -> Event:
        """Build from a RawStage dict (motorsport substage = race/GP).

        Stages use ``startDateTimestamp`` instead of ``startTimestamp`` and
        carry a ``winner`` instead of home/away teams.  There is no
        separate "full event" endpoint for stages, so the object is marked
        as fully loaded immediately.
        """
        ev = cls(
            id=raw.get("id", 0),
            slug=raw.get("slug", ""),
            name=raw.get("name", ""),
            start=timestamp_to_dt(raw.get("startDateTimestamp")),
            status=_status_from_raw(raw.get("status")),
        )
        ev._raw = raw

        # Delegate race construction to RaceData
        ev._race = RaceData._from_raw(raw, ev)

        return ev

    # -- Properties: eagerly available --------------------------------- #

    @property
    def match(self) -> Optional[MatchData]:
        """Match-specific data (home/away, results, details, incidents, …).

        Returns ``None`` for stage/race events.
        """
        return self._match

    @property
    def race(self) -> Optional[RaceData]:
        """Race/stage-specific data (results, details, …).

        Returns ``None`` for match/fight events.
        """
        return self._race

    @property
    def round(self) -> Optional[Round]:
        return self._round

    @property
    def season(self) -> Optional[Season]:
        return self._season

    @property
    def venue(self) -> Optional[Venue]:
        """Event venue (checks raw first, full-loads only if needed)."""
        if self._venue is None:
            from .venue import Venue
            raw_venue = self._raw.get("venue")
            if not raw_venue:
                self._load_full()
                raw_venue = self._raw.get("venue")
            if raw_venue:
                self._venue = Venue._from_raw(raw_venue)
        return self._venue

    # -- Internal ------------------------------------------------------ #

    def _load_full(self) -> None:
        if self._full_loaded:
            return
        if self._race is not None:
            # Stage event — use get_stage_details()
            logger.debug("Loading full data for stage '%s' (id=%s)", self.slug, self.id)
            self._raw.update(self._provider.get_stage_details(str(self.id)))
        else:
            # Match event — use get_event()
            logger.debug("Loading full data for event '%s' (id=%s)", self.slug, self.id)
            self._raw.update(self._provider.get_event(str(self.id)))
        self._full_loaded = True


# =====================================================================
# MatchData — match-specific data bundle
# =====================================================================

class MatchData:
    """Match-specific data: home/away teams, referee, results, details,
    periods, incidents, lineups, head-to-head, statistics, and momentum.

    Accessed via ``event.match``.  Only available for match/fight events,
    not for stage/race events.
    """

    def __init__(self, event: Event) -> None:
        self._event = event

        # Eagerly populated by _from_raw
        self._home: Optional[Competitor] = None
        self._away: Optional[Competitor] = None
        self._referee: Optional[Referee] = None
        self._results: Optional[MatchResults] = None

        # Lazy-loaded (require _load_full first)
        self._details: Optional[MatchDetails] = None
        self._periods: Optional[ParsedPeriods] = None

        # Lazy-loaded (require separate API calls)
        self._incidents: Optional[list[ParsedIncident]] = None
        self._lineups: Optional[EventLineups] = None
        self._statistics: Optional[list[PeriodStatistics]] = None
        self._h2h: Optional[list[Event]] = None
        self._momentum: Optional[Momentum] = None

    def __repr__(self) -> str:
        home = self._home.name if self._home else "?"
        away = self._away.name if self._away else "?"
        return f"<MatchData: {home} vs {away}>"

    # -- Construction -------------------------------------------------- #

    @classmethod
    def _from_raw(cls, raw: dict, event: Event) -> MatchData:
        """Build match data from a raw event dict.

        Eagerly parses home/away teams, referee, and results.
        """
        from .participant import Competitor, Referee

        match = cls(event)

        # Score + outcome
        parsed_score = get_display_score(raw)
        score = None
        if parsed_score:
            score = Score(home=parsed_score["home"], away=parsed_score["away"])
        match._results = MatchResults(
            score=score,
            outcome=get_event_outcome(raw),
            win_type=raw.get("winType"),
            final_round=raw.get("finalRound"),
        )

        # Participants
        if raw.get("homeTeam"):
            match._home = Competitor._from_raw_team(raw["homeTeam"])
        if raw.get("awayTeam"):
            match._away = Competitor._from_raw_team(raw["awayTeam"])
        if raw.get("referee"):
            match._referee = Referee._from_raw(raw["referee"])

        return match

    def _load_full(self) -> None:
        """Ensure the parent event's raw data is fully loaded."""
        self._event._load_full()

    # -- Properties: eagerly available --------------------------------- #

    @property
    def home(self) -> Optional[Competitor]:
        """Home team / competitor."""
        return self._home

    @property
    def away(self) -> Optional[Competitor]:
        """Away team / competitor."""
        return self._away

    @property
    def referee(self) -> Optional[Referee]:
        """Match referee."""
        if self._referee is None:
            self._load_full()
            from .participant import Referee
            raw_ref = self._event._raw.get("referee")
            if raw_ref:
                self._referee = Referee._from_raw(raw_ref)
        return self._referee

    # -- Properties: lazy-loaded from event raw ------------------------ #

    @property
    def results(self) -> MatchResults:
        """Match results (score, outcome, win type)."""
        if self._results is not None:
            return self._results
        self._load_full()
        parsed_score = get_display_score(self._event._raw)
        score = None
        if parsed_score:
            score = Score(home=parsed_score["home"], away=parsed_score["away"])
        self._results = MatchResults(
            score=score,
            outcome=get_event_outcome(self._event._raw),
            win_type=self._event._raw.get("winType"),
            final_round=self._event._raw.get("finalRound"),
        )
        return self._results

    @property
    def details(self) -> MatchDetails:
        """Extended match details — attendance, periods, gender, etc."""
        if self._details is not None:
            return self._details
        self._load_full()
        self._details = MatchDetails(
            attendance=self._event._raw.get("attendance"),
            periods=self.periods,
            gender=self._event._raw.get("gender"),
            first_to_serve=self._event._raw.get("firstToServe"),
            fight_type=self._event._raw.get("fightType"),
            weight_class=self._event._raw.get("weightClass"),
        )
        return self._details

    @property
    def periods(self) -> Optional[ParsedPeriods]:
        """Reconstructed period structure (from the event's score/time data)."""
        if self._periods is not None:
            return self._periods
        self._load_full()
        self._periods = parse_periods(self._event._raw)
        return self._periods

    # -- Properties: lazy-loaded (separate API calls) ------------------- #

    @property
    def incidents(self) -> list[ParsedIncident]:
        """Parsed incidents for this match (lazy, separate API call)."""
        if self._incidents is not None:
            return self._incidents
        logger.debug("Fetching incidents for event '%s' (id=%s)", self._event.slug, self._event.id)
        raw_incidents = self._event._provider.get_incidents(str(self._event.id))
        self._incidents = parse_incidents(raw_incidents)
        return self._incidents

    @property
    def lineups(self) -> Optional[EventLineups]:
        """Home and away lineups (lazy, separate API call)."""
        if self._lineups is not None:
            return self._lineups

        from .participant import Competitor

        logger.debug("Fetching lineups for event '%s' (id=%s)", self._event.slug, self._event.id)
        raw = self._event._provider.get_lineups(str(self._event.id))
        if not raw:
            return None

        home_lineup = None
        away_lineup = None
        if "home" in raw and raw["home"]:
            h = raw["home"]
            home_lineup = Lineup(
                players=[Competitor._from_raw_player(p) for p in h.get("players", [])],
                missing_players=[Competitor._from_raw_player(p) for p in h.get("missingPlayers", [])],
                formation=h.get("formation"),
            )
        if "away" in raw and raw["away"]:
            a = raw["away"]
            away_lineup = Lineup(
                players=[Competitor._from_raw_player(p) for p in a.get("players", [])],
                missing_players=[Competitor._from_raw_player(p) for p in a.get("missingPlayers", [])],
                formation=a.get("formation"),
            )

        self._lineups = EventLineups(home=home_lineup, away=away_lineup)
        return self._lineups

    @property
    def statistics(self) -> list[PeriodStatistics]:
        """Match statistics broken down by period (lazy, separate API call)."""
        if self._statistics is not None:
            return self._statistics
        logger.debug("Fetching statistics for event '%s' (id=%s)", self._event.slug, self._event.id)
        response = self._event._provider.get_event_statistics(str(self._event.id))
        self._statistics = [
            PeriodStatistics(
                period=ps.get("period", ""),
                groups=[
                    StatisticsGroup(
                        name=g.get("groupName", ""),
                        items=[
                            StatisticsItem._from_raw(item)
                            for item in g.get("statisticsItems", [])
                        ],
                    )
                    for g in ps.get("groups", [])
                ],
            )
            for ps in response.get("statistics", [])
        ]
        return self._statistics

    @property
    def h2h(self) -> list[Event]:
        """Head-to-head history (lazy, separate API call)."""
        if self._h2h is not None:
            return self._h2h
        custom_id = self._event._raw.get("customId")
        if not custom_id:
            logger.info("No customId on event '%s' — h2h unavailable", self._event.slug)
            self._h2h = []
            return self._h2h
        logger.debug("Fetching h2h for event '%s'", self._event.slug)
        response = self._event._provider.get_h2h_history(custom_id)
        self._h2h = [
            Event._from_raw_event(e)
            for e in response.get("events", [])
        ]
        return self._h2h

    @property
    def momentum(self) -> Optional[Momentum]:
        """Momentum graph data (lazy, separate API call).

        Returns ``None`` when no graph is available (e.g. MMA, not-started events).
        Each point has a ``minute`` and ``value`` (positive = home, negative = away).
        """
        if self._momentum is not None:
            return self._momentum
        logger.debug("Fetching momentum graph for event '%s' (id=%s)", self._event.slug, self._event.id)
        response = self._event._provider.get_event_graph(str(self._event.id))
        if not response or "graphPoints" not in response:
            return None
        points = [
            MomentumPoint(minute=p.get("minute", 0), value=p.get("value", 0))
            for p in response["graphPoints"]
        ]
        self._momentum = Momentum(
            points=points,
            period_time=response.get("periodTime"),
            period_count=response.get("periodCount"),
            overtime_length=response.get("overtimeLength"),
        )
        return self._momentum


# =====================================================================
# RaceData — stage/race-specific data bundle
# =====================================================================

class RaceData:
    """Race/stage-specific data: results and details.

    Accessed via ``event.race``.  Only available for stage/race events,
    not for match/fight events.
    """

    def __init__(self, event: Event) -> None:
        self._event = event

        self._results: Optional[RaceResults] = None
        self._details: Optional[StageDetails] = None

    def __repr__(self) -> str:
        return f"<RaceData: {self._event.name}>"

    # -- Construction -------------------------------------------------- #

    @classmethod
    def _from_raw(cls, raw: dict, event: Event) -> RaceData:
        """Build race data from a raw stage dict.

        Eagerly parses winner and race-info fields available in the raw
        dict (``info`` sub-dict for laps/lap record).
        """
        from .participant import Competitor

        race = cls(event)

        # Winner
        winner = None
        if raw.get("winner"):
            winner = Competitor._from_raw_team(raw["winner"])

        # Race stats from the info dict  (lapsCompleted, lapRecord)
        raw_info = raw.get("info")
        laps_completed = None
        lap_record = None
        if raw_info and isinstance(raw_info, dict):
            laps_completed = raw_info.get("lapsCompleted")
            lap_record = raw_info.get("lapRecord")

        race._results = RaceResults(
            winner=winner,
            laps_completed=laps_completed,
            lap_record=lap_record,
        )

        return race

    def _load_full(self) -> None:
        """Ensure the parent stage's raw data is fully loaded."""
        self._event._load_full()

    # -- Properties ---------------------------------------------------- #

    @property
    def results(self) -> RaceResults:
        """Race results (winner, standings, laps)."""
        if self._results is not None:
            return self._results
        self._results = RaceResults()
        return self._results

    @property
    def standings(self) -> list:
        """Competitor standings for this stage (lazy, separate API call).

        Returns a list of ``StandingsEntry`` from the stage standings endpoint.
        """
        # Attach to results if not yet populated
        if self._results and self._results.standings:
            return self._results.standings

        from .leaderboard import StandingsEntry

        logger.debug(
            "Fetching stage standings for '%s' (id=%s)",
            self._event.name, self._event.id,
        )
        raw_standings = self._event._provider.get_stage_standings_competitors(
            str(self._event.id)
        )
        entries = [StandingsEntry._from_raw(s) for s in raw_standings]

        # Rebuild results with standings included
        old = self._results or RaceResults()
        self._results = RaceResults(
            winner=old.winner,
            standings=entries,
            laps_completed=old.laps_completed,
            lap_record=old.lap_record,
        )
        return entries

    @property
    def details(self) -> StageDetails:
        """Extended stage details — circuit, conditions, etc."""
        if self._details is not None:
            return self._details
        self._load_full()
        raw_info = self._event._raw.get("info")
        if raw_info and isinstance(raw_info, dict):
            self._details = StageDetails(
                circuit=raw_info.get("circuit"),
                circuit_city=raw_info.get("circuitCity"),
                circuit_country=raw_info.get("circuitCountry"),
                circuit_length=raw_info.get("circuitLength"),
                laps=raw_info.get("laps"),
                race_distance=raw_info.get("raceDistance"),
                weather=raw_info.get("weather"),
                air_temperature=raw_info.get("airTemperature"),
                track_temperature=raw_info.get("trackTemperature"),
                humidity=raw_info.get("humidity"),
                track_condition=raw_info.get("trackCondition"),
                race_type=raw_info.get("raceType"),
                stage_type=raw_info.get("stageType"),
                discipline=raw_info.get("discipline"),
                departure_city=raw_info.get("departureCity"),
                arrival_city=raw_info.get("arrivalCity"),
            )
        else:
            self._details = StageDetails()
        return self._details


# =====================================================================
# Supporting dataclasses
# =====================================================================

@dataclass(frozen=True)
class Lineup:
    """One side's lineup in an event."""
    players: list[Competitor]
    missing_players: list[Competitor] = field(default_factory=list)
    formation: Optional[str] = None


@dataclass(frozen=True)
class EventLineups:
    """Both sides' lineups."""
    home: Optional[Lineup] = None
    away: Optional[Lineup] = None


# -- Results --------------------------------------------------------------- #

@dataclass(frozen=True)
class MatchResults:
    """Results for a normal event (match, fight, etc.)."""
    score: Optional[Score] = None
    outcome: Optional[str] = None           # "home", "away", "draw"
    # Fight-sport specifics (how the fight ended)
    win_type: Optional[str] = None          # "KO", "Submission", etc.
    final_round: Optional[int] = None


@dataclass(frozen=True)
class RaceResults:
    """Results for a stage event (race, GP, cycling stage, etc.)."""
    winner: Optional[Competitor] = None
    standings: list[StandingsEntry] = field(default_factory=list)
    laps_completed: Optional[int] = None
    lap_record: Optional[str] = None



# -- Details --------------------------------------------------------------- #

@dataclass(frozen=True)
class MatchDetails:
    """Context metadata for a normal event (match, fight, etc.)."""
    attendance: Optional[int] = None
    periods: Optional[ParsedPeriods] = None
    gender: Optional[Literal["M", "F", "X"]] = None
    first_to_serve: Optional[int] = None    # Tennis: 1 or 2
    # Fight-sport context
    fight_type: Optional[str] = None
    weight_class: Optional[str] = None


@dataclass(frozen=True)
class StageDetails:
    """Context metadata for a stage event (race, GP, cycling stage, etc.)."""
    # Circuit info
    circuit: Optional[str] = None
    circuit_city: Optional[str] = None
    circuit_country: Optional[str] = None
    circuit_length: Optional[float] = None  # meters
    laps: Optional[int] = None
    race_distance: Optional[int] = None     # meters
    # Conditions
    weather: Optional[str] = None
    air_temperature: Optional[float] = None
    track_temperature: Optional[float] = None
    humidity: Optional[float] = None
    track_condition: Optional[str] = None
    race_type: Optional[str] = None         # "Circuit", "Point-to-point"
    # Stage classification
    stage_type: Optional[str] = None        # "Mountain", "Sprint"
    discipline: Optional[str] = None
    # Cycling
    departure_city: Optional[str] = None
    arrival_city: Optional[str] = None



@dataclass(frozen=True)
class MomentumPoint:
    """A single point on the momentum graph."""
    minute: float
    value: int          # positive = home advantage, negative = away advantage


@dataclass(frozen=True)
class Momentum:
    """Momentum graph for an event."""
    points: list[MomentumPoint]
    period_time: Optional[int] = None       # e.g. 45 (football), 12 (NBA)
    period_count: Optional[int] = None      # e.g. 2 (football), 4 (NBA)
    overtime_length: Optional[int] = None


_COMPARE_WINNER: dict[int, str] = {1: "home", 2: "away", 3: "tied"}


@dataclass(frozen=True)
class StatisticsItem:
    """A single statistic row (e.g. 'Ball possession')."""
    key: str                                    # e.g. "ballPossession"
    name: str                                   # display name, e.g. "Ball possession"
    home: str                                   # formatted string, e.g. "54%"
    away: str
    home_value: Optional[float] = None          # numeric value
    away_value: Optional[float] = None
    home_total: Optional[float] = None          # denominator for ratio stats (NBA 3-pointers, tennis serves…)
    away_total: Optional[float] = None
    winner: Optional[str] = None                # "home", "away", or "tied"
    stat_type: Optional[str] = None             # "positive" or "negative"

    @classmethod
    def _from_raw(cls, raw: dict) -> StatisticsItem:
        return cls(
            key=raw.get("key", ""),
            name=raw.get("name", ""),
            home=raw.get("home", ""),
            away=raw.get("away", ""),
            home_value=raw.get("homeValue"),
            away_value=raw.get("awayValue"),
            home_total=raw.get("homeTotal"),
            away_total=raw.get("awayTotal"),
            winner=_COMPARE_WINNER.get(raw.get("compareCode", 0)),
            stat_type=raw.get("statisticsType"),
        )


@dataclass(frozen=True)
class StatisticsGroup:
    """A named group of statistics items (e.g. 'Match overview', 'Shots')."""
    name: str
    items: list[StatisticsItem] = field(default_factory=list)


@dataclass(frozen=True)
class PeriodStatistics:
    """Statistics for one period (e.g. 'ALL', '1ST', '2ND')."""
    period: str
    groups: list[StatisticsGroup] = field(default_factory=list)


# Forward refs for dataclass fields (Lineup, RaceResults)
from .participant import Competitor  # noqa: E402
from .leaderboard import StandingsEntry  # noqa: E402
