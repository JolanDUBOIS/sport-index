"""Builders for minimal domain payloads used by the offline (Tier 1) tests.

Rather than recorded API responses, these construct the smallest payload that exercises the
behaviour under test, so a test reads as a statement about the domain rather than about
Sofascore.
"""

from __future__ import annotations

from typing import Any

from sportindex.api_client.models import (
    StageTier,
    _CategoryData,
    _EventData,
    _ManagerData,
    _PlayerData,
    _SeasonData,
    _SportData,
    _StageData,
    _TeamData,
    _UniqueStageData,
    _UniqueTournamentData,
    _VenueData,
)

FOOTBALL = _SportData(id=1, name="Football", slug="football")
MOTORSPORT = _SportData(id=11, name="Motorsport", slug="motorsport")


# --- payload builders -------------------------------------------------------------------

def category(id: int = 7, name: str = "France", sport: _SportData = FOOTBALL) -> _CategoryData:
    return _CategoryData(id=id, name=name, slug=name.lower().replace(" ", "-"), sport=sport)


def team(id: int = 1, name: str = "Team", sport: _SportData = FOOTBALL, **kw: Any) -> _TeamData:
    return _TeamData(id=id, slug=name.lower().replace(" ", "-"), name=name, sport=sport, **kw)


def player(id: int = 1, name: str = "Player", **kw: Any) -> _PlayerData:
    return _PlayerData(id=id, slug=name.lower().replace(" ", "-"), name=name, **kw)


def manager(id: int = 1, name: str = "Manager", **kw: Any) -> _ManagerData:
    return _ManagerData(id=id, slug=name.lower().replace(" ", "-"), name=name, **kw)


def venue(id: int = 1, name: str = "Stadium", **kw: Any) -> _VenueData:
    return _VenueData(id=id, slug=name.lower().replace(" ", "-"), name=name, **kw)


def tournament(id: int = 34, name: str = "Ligue 1") -> _UniqueTournamentData:
    return _UniqueTournamentData(id=id, slug=name.lower().replace(" ", "-"), name=name, category=category())


def unique_stage(id: int = 40, name: str = "Formula 1") -> _UniqueStageData:
    return _UniqueStageData(id=id, slug=name.lower().replace(" ", "-"), name=name,
                            category=category(name="International", sport=MOTORSPORT))


def season(id: int = 61736, name: str = "Ligue 1 24/25", **kw: Any) -> _SeasonData:
    return _SeasonData(id=id, name=name, **kw)


def stage(id: int = 1, name: str = "Race", tier: StageTier | None = StageTier.RACE,
          start: int | None = 1700000000, **kw: Any) -> _StageData:
    payload: dict[str, Any] = {
        "id": id,
        "slug": name.lower().replace(" ", "-"),
        "name": name,
        **kw,
    }
    if tier is not None:
        payload["type"] = {"id": int(tier), "name": tier.name.replace("_", " ").title()}
    if start is not None:
        payload["startDateTimestamp"] = start
    return _StageData.model_validate(payload)


def match(id: int = 1, home: _TeamData | None = None, away: _TeamData | None = None,
          start: int = 1700000000, score: Any = None, **kw: Any) -> _EventData:
    home = home or team(1, "Home")
    away = away or team(2, "Away")
    payload: dict[str, Any] = {
        "id": id,
        "customId": f"c{id}",
        "slug": f"{home.slug}-{away.slug}",
        "startTimestamp": start,
        "homeTeam": home.model_dump(by_alias=True),
        "awayTeam": away.model_dump(by_alias=True),
        **kw,
    }
    if score is not None:
        payload["homeScore"] = {"display": score}
        payload["awayScore"] = {"display": score}
    return _EventData.model_validate(payload)
