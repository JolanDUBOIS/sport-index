from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal

from . import logger
from .core import BaseModel, Score


@dataclass(frozen=True)
class Period:
    key: str # Used in Scores
    type: Literal["normal", "overtime", "tiebreak", "penalties"] # Specific addition of this package, not present in API, more will be added if discovered
    label: Optional[str] = None
    score: Optional[Score] = None
    time: Optional[int] = None
    default_time: Optional[int] = None # In case of period with subperiods (e.g. football overtime), this is the default time for one subperiod
    extra_time: Optional[tuple[int, ...]] = None

@dataclass(frozen=True)
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
            logger.error(f"Event {_raw.get('id')} does not have defaultPeriodCount.")
            raise ValueError(f"Event {_raw.get('id')} does not have defaultPeriodCount.")

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
