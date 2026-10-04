"""Event search: matches and stages found through the provider's general search.

Payloads follow the shape of the provider's /search/all results, which mix competitions,
matches ("event") and event-level stages ("stage").
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from sportindex.api_client.models import _SearchResultData
from sportindex.domain import Event, MatchEvent, StageEvent

SPORT = {"id": 1, "slug": "sport", "name": "Sport"}
CATEGORY = {"id": 1, "name": "Category", "slug": "category", "sport": SPORT}


def competition_result(id: int, score: float) -> dict[str, Any]:
    return {"type": "uniqueTournament", "score": score,
            "entity": {"id": id, "name": "Competition", "slug": "competition", "category": CATEGORY}}


def stage_result(id: int, start: int, score: float) -> dict[str, Any]:
    # A stage search result carries its start as "startTimestamp", and no tier.
    return {"type": "stage", "score": score,
            "entity": {"id": id, "name": "Stage", "slug": "stage", "startTimestamp": start, "category": CATEGORY}}


def match_result(id: int, score: float) -> dict[str, Any]:
    side = {"name": "Side", "slug": "side", "sport": SPORT}
    return {"type": "event", "score": score,
            "entity": {"id": id, "customId": f"c{id}", "name": "Home - Away", "slug": "home-away",
                       "startTimestamp": 1700000000,
                       "homeTeam": {"id": 1, **side}, "awayTeam": {"id": 2, **side}}}


RESULTS = [
    competition_result(10, score=42.4),
    stage_result(20, start=1751709414, score=42.3),
    match_result(30, score=25.7),
    stage_result(40, start=1783178942, score=0),
]


class FakeProvider:
    """Serves one page of search results; anything else the domain asks for is a failure."""

    def search_all(self, query: str, page: int = 0) -> list[_SearchResultData]:
        return [_SearchResultData.model_validate(r) for r in RESULTS] if page == 0 else []


def test_event_search_returns_matches_and_stages_but_not_competitions():
    found = Event.search("query", FakeProvider())

    assert [e.id for e in found] == ["stg:20", "mch:30", "stg:40"]
    assert [type(e) for e in found] == [StageEvent, MatchEvent, StageEvent]
    assert found.get_score("stg:20") == pytest.approx(42.3)


def test_stage_search_keeps_only_stages():
    assert [e.id for e in StageEvent.search("query", FakeProvider())] == ["stg:20", "stg:40"]


def test_match_search_keeps_only_matches():
    assert [e.id for e in MatchEvent.search("query", FakeProvider())] == ["mch:30"]


def test_a_stage_found_by_search_is_dated_without_a_request():
    stage = StageEvent.search("query", FakeProvider())[1]
    assert stage.start == datetime(2026, 7, 4, 15, 29, 2, tzinfo=UTC)


def test_an_empty_query_is_rejected():
    with pytest.raises(ValueError):
        Event.search("  ", FakeProvider())
