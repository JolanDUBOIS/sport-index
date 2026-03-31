from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from pydantic import Field, ValidationInfo, model_validator

from .base import BaseSchema

if TYPE_CHECKING:
    from .referee import _RefereeData
    from .primitives import EventStatus, Score
    from .team import _TeamData
    from .tournament import _SeasonData, _TournamentData
    from .venue import _VenueData


# =====================================================================
# Primitives
# =====================================================================

class Round(BaseSchema):
    name: str | None = None
    slug: str | None = None
    value: int | None = Field(default=None, alias="round")


class MatchPeriod(BaseSchema):
    key: str                             # e.g. "period1", "overtime", "penalties", "period2TieBreak"
    type: str                            # "normal", "overtime", "tiebreak", "penalties"
    label: str | None = None             # Display label, e.g. "1st Half", "Overtime"
    score: Score | None = None
    time: int | None = None              # Actual elapsed time for this period (if known)
    default_time: int | None = None
    extra_time: list[int] | None = None  # Injury/stoppage time added in this period


class _PeriodsData(BaseSchema):
    default_count: int | None = None
    periods: list[MatchPeriod] = Field(default_factory=list)


# =====================================================================
# Extra Data
# =====================================================================

class _FightExtraData(BaseSchema):
    fight_type: str | None = None
    weight_class: str | None = None
    win_type: str | None = None
    final_round: int | None = None
    order: list[int] = Field(default_factory=list)


class _RacketExtraData(BaseSchema):
    first_to_serve: int | None = None


# =====================================================================
# Event Team
# =====================================================================

class _EventTeamData(BaseSchema):
    team: _TeamData
    seed: str | int | None = None
    ranking: int | None = None
    score: int | str | None = None


# =====================================================================
# Event
# =====================================================================

class _EventData(BaseSchema):
    id: int
    custom_id: str
    slug: str
    gender: str | None = None
    start: datetime = Field(alias="startTimestamp")
    round: Round | None = Field(default=None, alias="roundInfo")
    season: _SeasonData | None = None
    tournament: _TournamentData | None = None

    attendance: int | None = None
    status: EventStatus | None = None
    previous_leg_event_id: int | None = None
    winner_code: int | None = None  # 1=home, 2=away, 3=draw

    # Teams / participants
    home: _EventTeamData
    away: _EventTeamData
    referee: _RefereeData | None = None
    venue: _VenueData | None = None

    # Extra & Periods
    extra: _FightExtraData | _RacketExtraData | None = None
    periods: _PeriodsData | None = None

    @model_validator(mode='before')
    @classmethod
    def reshape_flat_api_fields(cls, data: Any, info: ValidationInfo) -> Any:
        if not isinstance(data, dict):
            return data

        if info.context and info.context.get("preprocessed"):
            return data

        # 1. Reshape 'Extra'
        if any(k in data for k in ("fightType", "weightClass", "winType", "finalRound")):
            data["extra"] = {
                "fightType": data.get("fightType"),
                "weightClass": data.get("weightClass"),
                "winType": data.get("winType"),
                "finalRound": data.get("finalRound"),
                "order": data.get("order", [])
            }
        elif "firstToServe" in data:
            data["extra"] = {"firstToServe": data.get("firstToServe")}

        # 2. Reshape 'Periods'
        if "defaultPeriodCount" in data:
            default_count = data["defaultPeriodCount"]
            home_score = data.get("homeScore") or {}
            away_score = data.get("awayScore") or {}
            time_info = data.get("time") or {}
            period_labels = data.get("periods") or {}

            default_period_time = data.get("defaultPeriodLength")
            default_overtime_time = data.get("defaultOvertimeLength")

            periods_list = []

            # Normal periods
            for k in range(1, default_count + 1):
                key = f"period{k}"
                score_dict = None
                if key in home_score and key in away_score:
                    score_dict = {"home": home_score[key], "away": away_score[key]}

                extra_time_val = time_info.get(f"injuryTime{k}")

                periods_list.append({
                    "key": key,
                    "type": "normal",
                    "label": period_labels.get(key),
                    "score": score_dict,
                    "time": time_info.get(key),
                    "defaultTime": default_period_time,
                    "extraTime": [extra_time_val] if extra_time_val else None,
                })

            # Tiebreak periods
            for k in range(1, default_count + 1):
                key = f"period{k}TieBreak"
                if key in home_score and key in away_score:
                    score_dict = {"home": home_score[key], "away": away_score[key]}
                    
                    label = period_labels.get(key)
                    if not label:
                        parent_label = period_labels.get(f"period{k}")
                        label = f"{parent_label} Tie-Break" if parent_label else None
                        
                    periods_list.append({
                        "key": key,
                        "type": "tiebreak",
                        "label": label,
                        "score": score_dict,
                        "time": None,
                        "defaultTime": None,
                        "extraTime": None,
                    })

            # Overtime
            if "overtime" in home_score and "overtime" in away_score:
                score_dict = {"home": home_score["overtime"], "away": away_score["overtime"]}

                extra_time_list = []
                for time_key, time_val in time_info.items():
                    if time_key.startswith("injuryTime"):
                        try:
                            idx = int(time_key.replace("injuryTime", ""))
                        except ValueError:
                            continue
                        if idx > default_count and time_val is not None:
                            extra_time_list.append(time_val)

                periods_list.append({
                    "key": "overtime",
                    "type": "overtime",
                    "label": period_labels.get("overtime", "Overtime"),
                    "score": score_dict,
                    "time": time_info.get("overtime"),
                    "defaultTime": default_overtime_time,
                    "extraTime": extra_time_list if extra_time_list else None,
                })

            # Penalty shootout
            if "penalties" in home_score and "penalties" in away_score:
                score_dict = {"home": home_score["penalties"], "away": away_score["penalties"]}
                periods_list.append({
                    "key": "penalties",
                    "type": "penalties",
                    "label": period_labels.get("penalties", "Penalty Shootout"),
                    "score": score_dict,
                    "time": None,
                    "defaultTime": None,
                    "extraTime": None,
                })

            # Mount the final periods dict
            data["periods"] = {
                "defaultCount": default_count,
                "periods": periods_list
            }

        # 3. Reshape 'Home' and 'Away' Team Data
        for side in ("home", "away"):
            raw_score = data.get(f"{side}Score")            
            data[side] = {
                "team": data.get(f"{side}Team"),
                "seed": data.get(f"{side}TeamSeed"),
                "ranking": data.get(f"{side}TeamRanking"),
                "score": raw_score.get("display") if isinstance(raw_score, dict) else None
            }

        return data
