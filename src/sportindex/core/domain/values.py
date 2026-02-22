"""
Value objects — small frozen dataclasses with no identity or lazy loading.

These replace the TypedDicts/raw dicts at the domain boundary so that
the consumer never touches a dict after leaving the provider layer.
All fields use snake_case.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# =====================================================================
# Common value objects
# =====================================================================

@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float


@dataclass(frozen=True)
class Amount:
    """Monetary value (transfer fee, salary, prize money)."""
    value: float
    currency: str          # e.g. "EUR", "USD"


@dataclass(frozen=True)
class Status:
    """Event or stage status."""
    code: int
    type: str              # e.g. "finished", "inprogress", "notstarted"
    description: str       # e.g. "Ended", "1st half"


@dataclass(frozen=True)
class Cards:
    """Card statistics for a referee."""
    yellow: int
    red: int
    yellow_red: int


@dataclass(frozen=True)
class Promotion:
    """Promotion / relegation info in a standings row."""
    id: int
    text: str              # e.g. "Champions League", "Relegation"


@dataclass(frozen=True)
class Score:
    """Simple home/away score pair."""
    home: int
    away: int


@dataclass(frozen=True)
class Round:
    """Event round information."""
    number: Optional[int]
    name: Optional[str]
    slug: Optional[str]


@dataclass(frozen=True)
class Performance:
    """Manager career performance stats."""
    total: int
    wins: int
    draws: int
    losses: int
    goals_scored: int
    goals_conceded: int
    total_points: int


# =====================================================================
# Conversion helpers — raw dicts → value objects
# =====================================================================

def _amount_from_raw(raw: dict | None) -> Optional[Amount]:
    if not raw or "value" not in raw:
        return None
    return Amount(value=raw["value"], currency=raw.get("currency", ""))


def _status_from_raw(raw: dict | None) -> Optional[Status]:
    if not raw or "code" not in raw:
        return None
    return Status(
        code=raw["code"],
        type=raw.get("type", ""),
        description=raw.get("description", ""),
    )


def _coordinates_from_raw(raw: dict | None) -> Optional[Coordinates]:
    if not raw or "latitude" not in raw:
        return None
    return Coordinates(latitude=raw["latitude"], longitude=raw["longitude"])


def _cards_from_raw(raw: dict | None) -> Optional[Cards]:
    """Build Cards from a raw referee dict (card fields are top-level)."""
    if raw is None:
        return None
    yellow = raw.get("yellowCards", 0)
    red = raw.get("redCards", 0)
    yellow_red = raw.get("yellowRedCards", 0)
    if yellow == 0 and red == 0 and yellow_red == 0:
        return None
    return Cards(yellow=yellow, red=red, yellow_red=yellow_red)


def _promotion_from_raw(raw: dict | None) -> Optional[Promotion]:
    if not raw or "id" not in raw:
        return None
    return Promotion(id=raw["id"], text=raw.get("text", ""))


def _score_from_raw(home_score: dict | None, away_score: dict | None) -> Optional[Score]:
    """Extract the display score from homeScore/awayScore dicts."""
    if not home_score or not away_score:
        return None
    if "display" in home_score and "display" in away_score:
        return Score(home=home_score["display"], away=away_score["display"])
    return None


def _round_from_raw(raw: dict | None) -> Optional[Round]:
    if not raw:
        return None
    return Round(
        number=raw.get("number"),
        name=raw.get("name"),
        slug=raw.get("slug"),
    )


def _performance_from_raw(raw: dict | None) -> Optional[Performance]:
    if not raw or "total" not in raw:
        return None
    return Performance(
        total=raw["total"],
        wins=raw.get("wins", 0),
        draws=raw.get("draws", 0),
        losses=raw.get("losses", 0),
        goals_scored=raw.get("goalScored", 0),
        goals_conceded=raw.get("goalConceded", 0),
        total_points=raw.get("totalPoints", 0),
    )
