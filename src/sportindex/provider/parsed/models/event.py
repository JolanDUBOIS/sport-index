from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict, TYPE_CHECKING

from .base import BaseParsedModel
from .parsers import parse_timestamp
if TYPE_CHECKING:
    from .referee import ParsedReferee
    from .team import ParsedTeam
    from .tournament import ParsedSeason, ParsedTournament
    from .venue import ParsedVenue
    from sportindex.provider.raw.models import (
        RawRound, RawStatus, RawEvent
    )


# =====================================================================
# Primitives
# =====================================================================

@dataclass
class ParsedRound(BaseParsedModel):
    name: str
    slug: str
    round: int

    @classmethod
    def _parse(cls, raw: RawRound) -> ParsedRound:
        return cls(**raw)


# =====================================================================
# Event
# =====================================================================

@dataclass
class ParsedEvent(BaseParsedModel):
    id: int
    customId: str
    slug: str
    gender: str
    start: datetime
    roundInfo: ParsedRound
    season: ParsedSeason
    tournament: ParsedTournament

    attendance: int
    status: RawStatus
    previousLegEventId: int
    winnerCode: int  # 1=home, 2=away, 3=draw 

    # Teams / participants
    home: EventTeam
    away: EventTeam
    referee: ParsedReferee
    venue: ParsedVenue

    # Extra info for specific sports
    extra: ParsedExtra

    # Parsed periods
    parsedPeriods: ParsedPeriods

    @classmethod
    def _parse(cls, raw: RawEvent) -> ParsedEvent:
        from .referee import ParsedReferee
        from .tournament import ParsedSeason, ParsedTournament
        from .venue import ParsedVenue
        return cls(
            id=raw.get("id"),
            customId=raw.get("customId"),
            slug=raw.get("slug"),
            gender=raw.get("gender"),
            start=parse_timestamp(raw.get("startTimestamp")),
            roundInfo=ParsedRound.from_raw(raw.get("roundInfo")),
            season=ParsedSeason.from_raw(raw.get("season")),
            tournament=ParsedTournament.from_raw(raw.get("tournament")),
            attendance=raw.get("attendance"),
            status=raw.get("status"),
            previousLegEventId=raw.get("previousLegEventId"),
            winnerCode=raw.get("winnerCode"),
            home=EventTeam.from_raw(raw, "home"),
            away=EventTeam.from_raw(raw, "away"),
            referee=ParsedReferee.from_raw(raw.get("referee")),
            venue=ParsedVenue.from_raw(raw.get("venue")),
            extra=parse_extra(raw),
            parsedPeriods=ParsedPeriods.from_raw(raw)
        )


# =====================================================================
# Event Team
# =====================================================================

@dataclass
class EventTeam:
    team: ParsedTeam
    seed: int
    ranking: int
    score: int

    @classmethod
    def from_raw(cls, raw: RawEvent, side: str) -> EventTeam:
        from .team import ParsedTeam
        return cls(
            team=ParsedTeam.from_raw(raw.get(f"{side}Team")),
            seed=raw.get(f"{side}TeamSeed"),
            ranking=raw.get(f"{side}TeamRanking"),
            score=raw.get(f"{side}Score", {}).get("display"),
        )


# =====================================================================
# Periods & scoring
# =====================================================================

@dataclass
class ParsedScore(BaseParsedModel):
    home: int
    away: int

@dataclass
class ParsedPeriod(BaseParsedModel):
    key: str                                # e.g. "period1", "overtime", "penalties", "period2TieBreak"
    type: str                               # "normal", "overtime", "tiebreak", "penalties"
    label: str                              # Display label, e.g. "1st Half", "Overtime"
    score: ParsedScore
    time: int                               # Actual elapsed time for this period (if known)
    defaultTime: int
    extraTime: list[int]                    # Injury/stoppage time added in this period

@dataclass
class ParsedPeriods(BaseParsedModel):
    defaultCount: int
    periods: list[ParsedPeriod]

    @classmethod
    def _parse(cls, raw: RawEvent) -> ParsedPeriods | None:
        if "defaultPeriodCount" not in raw:
            return None

        home_score = raw.get("homeScore") or {}
        away_score = raw.get("awayScore") or {}
        time_info = raw.get("time") or {}
        period_labels = raw.get("periods") or {}

        default_count = raw["defaultPeriodCount"]
        default_period_time = raw.get("defaultPeriodLength")
        default_overtime_time = raw.get("defaultOvertimeLength")

        periods: list[ParsedPeriod] = []

        # --- Normal periods ---
        for k in range(1, default_count + 1):
            key = f"period{k}"
            score = None
            if key in home_score and key in away_score:
                score = ParsedScore(home=home_score[key], away=away_score[key])

            extra_time_val = time_info.get(f"injuryTime{k}")

            periods.append(ParsedPeriod(
                key=key,
                type="normal",
                label=period_labels.get(key),
                score=score,
                time=time_info.get(key),
                defaultTime=default_period_time,
                extraTime=[extra_time_val] if extra_time_val else None,
            ))

        # --- Tiebreak periods (tennis) ---
        for k in range(1, default_count + 1):
            key = f"period{k}TieBreak"
            if key in home_score and key in away_score:
                score = ParsedScore(home=home_score[key], away=away_score[key])
                
                # Build label: use explicit label, or append " Tie-Break" to parent period label
                label = period_labels.get(key)
                if not label:
                    parent_label = period_labels.get(f"period{k}")
                    label = f"{parent_label} Tie-Break" if parent_label else None
                    
                periods.append(ParsedPeriod(
                    key=key,
                    type="tiebreak",
                    label=label,
                    score=score,
                    time=None,
                    defaultTime=None,
                    extraTime=None,
                ))

        # --- Overtime ---
        if "overtime" in home_score and "overtime" in away_score:
            score = ParsedScore(home=home_score["overtime"], away=away_score["overtime"])

            # Collect injury times for overtime periods
            extra_time_list: list[int] = []
            for time_key, time_val in time_info.items():
                if time_key.startswith("injuryTime"):
                    try:
                        idx = int(time_key.removeprefix("injuryTime"))
                    except ValueError:
                        continue
                    if idx > default_count and time_val is not None:
                        extra_time_list.append(time_val)

            periods.append(ParsedPeriod(
                key="overtime",
                type="overtime",
                label=period_labels.get("overtime", "Overtime"),
                score=score,
                time=time_info.get("overtime"),
                defaultTime=default_overtime_time,
                extraTime=extra_time_list if extra_time_list else None,
            ))

        # --- Penalty shootout ---
        if "penalties" in home_score and "penalties" in away_score:
            score = ParsedScore(home=home_score["penalties"], away=away_score["penalties"])
            periods.append(ParsedPeriod(
                key="penalties",
                type="penalties",
                label=period_labels.get("penalties", "Penalty Shootout"),
                score=score,
                time=None,
                defaultTime=None,
                extraTime=None,
            ))

        return cls(
            defaultCount=default_count,
            periods=periods,
        )


# =====================================================================
# Sport-specific extra info
# =====================================================================

@dataclass
class ParsedFightExtra(BaseParsedModel):
    fightType: str
    weightClass: str
    winType: str
    finalRound: int
    order: list[int]

@dataclass
class ParsedRacketExtra(BaseParsedModel):
    firstToServe: int

ParsedExtra = ParsedFightExtra | ParsedRacketExtra

def parse_extra(raw: RawEvent) -> ParsedExtra | None:
    """Parse sport-specific extra info (fight or racket)."""
    # Fight sports
    if any(raw.get(k) is not None for k in ("fightType", "weightClass", "winType", "finalRound")):
        return ParsedFightExtra(
            fightType=raw.get("fightType"),
            weightClass=raw.get("weightClass"),
            winType=raw.get("winType"),
            finalRound=raw.get("finalRound"),
            order=raw.get("order", []),
        )
    # Racket sports
    if raw.get("firstToServe") is not None:
        return ParsedRacketExtra(firstToServe=raw["firstToServe"])
    return None
