"""Event search: matches and stages found by name, cycling races among them.

The provider's search returns a cycling race such as the Tour de France as a "stage" result,
one per edition: in its model the race is an event of the season of a competition named
after the discipline ("Cycling Men"), not a competition of its own.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from sportindex.api_client.models import _SearchResultData
from sportindex.domain import Competition, Event, MatchEvent, StageEvent

CYCLING = {"id": 65, "slug": "cycling", "name": "Cycling"}
FOOTBALL = {"id": 1, "slug": "football", "name": "Football"}


def tour_de_france(id: int, year: int, start: int, score: float) -> dict[str, Any]:
    return {
        "type": "stage",
        "score": score,
        "entity": {
            "id": id,
            "name": "Tour de France",
            "slug": "tour-de-france",
            "description": f"Tour de France - {year}",
            "startTimestamp": start,
            "category": {"id": 1458, "name": "International", "slug": "international", "sport": CYCLING},
            "country": {"alpha2": "FR", "name": "France", "slug": "france"},
        },
    }


# Trimmed from the provider's response to /search/all?q=tour de france.
RESULTS: list[dict[str, Any]] = [
    {
        "type": "uniqueTournament",
        "score": 42.426407,
        "entity": {
            "id": 19349,
            "name": "Pro Tour Paris  France 2022  Women ",
            "slug": "pro-tour-paris-france-2022-women",
            "category": {
                "id": 290, "name": "International", "slug": "international",
                "sport": {"id": 34, "slug": "beach-volley", "name": "Beach volley"},
            },
        },
    },
    tour_de_france(210217, 2025, 1751709414, 42.26999),
    {
        "type": "event",
        "score": 25.703938,
        "entity": {
            "id": 15798548,
            "customId": "CJsFMic",
            "name": "Racing Club de France - Tours FC",
            "slug": "racing-club-de-france-tours-fc",
            "startTimestamp": 484927200,
            "homeTeam": {"id": 271880, "name": "Racing Club de France", "slug": "racing-club-de-france", "sport": FOOTBALL},
            "awayTeam": {"id": 1727, "name": "Tours FC", "slug": "tours-fc", "sport": FOOTBALL},
            "homeScore": {"display": 3},
            "awayScore": {"display": 1},
        },
    },
    tour_de_france(220828, 2026, 1783178942, 0),
]


class FakeProvider:
    """Serves one page of search results; anything else the domain asks for is a failure."""

    def search_all(self, query: str, page: int = 0) -> list[_SearchResultData]:
        return [_SearchResultData.model_validate(r) for r in RESULTS] if page == 0 else []


def test_event_search_finds_races_and_matches_but_not_competitions():
    found = Event.search("Tour de France", FakeProvider())

    assert [e.id for e in found] == ["stg:210217", "mch:15798548", "stg:220828"]
    assert [type(e) for e in found] == [StageEvent, MatchEvent, StageEvent]
    assert found.get_score("stg:210217") == pytest.approx(42.26999)


def test_stage_search_keeps_only_stages():
    assert [e.id for e in StageEvent.search("Tour de France", FakeProvider())] == ["stg:210217", "stg:220828"]


def test_match_search_keeps_only_matches():
    assert [e.id for e in MatchEvent.search("Tour de France", FakeProvider())] == ["mch:15798548"]


def test_a_race_found_by_search_is_dated_without_a_request():
    tour_2026 = StageEvent.search("Tour de France", FakeProvider())[1]
    assert tour_2026.start == datetime(2026, 7, 4, 15, 29, 2, tzinfo=UTC)


def test_the_tour_is_not_a_competition():
    found = Competition.search("Tour de France", FakeProvider())
    assert [c.id for c in found] == ["trnc:19349"]


def test_an_empty_query_is_rejected():
    with pytest.raises(ValueError):
        Event.search("  ", FakeProvider())
