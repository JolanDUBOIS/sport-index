"""Tennis point-by-point: every point of a match, set by set and game by game.

Built from games of the provider's response to /event/17190001/point-by-point, which lists
sets and games newest first and points in playing order.
"""

from __future__ import annotations

from typing import Any

from sportindex.api_client.models import TennisSet, _PointByPointResponse
from sportindex.domain import MatchEvent
from sportindex.exceptions import ProviderNotFoundError

from factories import match


def point(home: str, away: str, description: int = 0, home_type: int = 1, away_type: int = 5) -> dict[str, Any]:
    return {"homePoint": home, "awayPoint": away, "pointDescription": description,
            "homePointType": home_type, "awayPointType": away_type}


def game(number: int, points: list[dict[str, Any]], home: int, away: int, serving: int, scoring: int) -> dict[str, Any]:
    return {"game": number, "points": points,
            "score": {"homeScore": home, "awayScore": away, "serving": serving, "scoring": scoring}}


PAYLOAD: dict[str, Any] = {"pointByPoint": [
    {"set": 2, "games": [
        game(1, [point("15", "0"), point("15", "15"), point("30", "15"), point("40", "15")],
             home=1, away=0, serving=1, scoring=1),
    ]},
    {"set": 1, "games": [
        game(2, [point("0", "15"), point("15", "15"), point("15", "30"), point("15", "40"),
                 point("30", "40"), point("40", "40"), point("A", "40"), point("40", "40"), point("40", "A")],
             home=0, away=2, serving=1, scoring=2),
        game(1, [point("0", "15"), point("15", "15"), point("30", "15"), point("30", "30", description=1),
                 point("30", "40", description=1)],
             home=0, away=1, serving=2, scoring=2),
    ]},
]}


class FakeProvider:
    """Serves the point-by-point payload, or a 404, counting requests."""

    def __init__(self, payload: dict[str, Any] | None) -> None:
        self._payload = payload
        self.requests = 0

    def get_event_point_by_point(self, event_id: int) -> _PointByPointResponse:
        self.requests += 1
        if self._payload is None:
            raise ProviderNotFoundError("404")
        return _PointByPointResponse.model_validate(self._payload)


def test_the_payload_parses_into_sets_games_and_points():
    tennis_set = _PointByPointResponse.model_validate(PAYLOAD).point_by_point[1]

    assert isinstance(tennis_set, TennisSet)
    assert tennis_set.number == 1
    advantage_game = tennis_set.games[0]
    assert advantage_game.number == 2
    assert [(p.home_point, p.away_point) for p in advantage_game.points][-3:] == [("A", "40"), ("40", "40"), ("40", "A")]
    assert (advantage_game.score.home_score, advantage_game.score.away_score) == (0, 2)
    assert (advantage_game.score.serving, advantage_game.score.scoring) == (1, 2)
    assert tennis_set.games[1].points[3].point_description == 1


def test_sets_and_games_come_in_playing_order():
    sets = MatchEvent(match(17190001), FakeProvider(PAYLOAD)).point_by_point

    assert [s.number for s in sets] == [1, 2]
    assert [g.number for g in sets[0].games] == [1, 2]


def test_points_keep_their_playing_order():
    first_game = MatchEvent(match(17190001), FakeProvider(PAYLOAD)).point_by_point[0].games[0]
    assert [(p.home_point, p.away_point) for p in first_game.points] == [
        ("0", "15"), ("15", "15"), ("30", "15"), ("30", "30"), ("30", "40"),
    ]


def test_a_match_without_point_by_point_has_an_empty_one():
    assert MatchEvent(match(1), FakeProvider(None)).point_by_point == []


def test_point_by_point_is_fetched_on_every_access():
    provider = FakeProvider(PAYLOAD)
    event = MatchEvent(match(17190001), provider)

    first = event.point_by_point
    second = event.point_by_point

    assert provider.requests == 2
    assert first == second
