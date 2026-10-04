"""Fixtures for teams and athletes, and the athlete's next-event fallback.

The provider's fixtures endpoint returns 404 for individual-sport athletes even when a match
is scheduled; the scheduled match is only reachable through the near-events endpoint. Teams
are served by the fixtures endpoint alone.
"""

from __future__ import annotations

from typing import Any

from factories import match, team

from sportindex.api_client.models import (
    _EventsResponse,
    _NearEventsResponse,
    _SportData,
)
from sportindex.domain import Athlete, Event, Team
from sportindex.exceptions import FetchError, ProviderNotFoundError

TENNIS = _SportData(id=5, name="Tennis", slug="tennis")


def tennis_player(id: int = 157754, name: str = "Aryna Sabalenka"):
    return team(id, name, sport=TENNIS, player_team_info={"id": 115})


def raw_event(id: int, home: str, away: str) -> dict[str, Any]:
    """A tennis event as the provider sends it, trimmed to the fields parsing requires."""
    def side(team_id: int, name: str) -> dict[str, Any]:
        return {"id": team_id, "name": name, "slug": name.lower().replace(" ", "-"),
                "type": 1, "sport": TENNIS.model_dump()}
    return {
        "id": id,
        "customId": f"c{id}",
        "slug": f"{home}-{away}".lower().replace(" ", "-"),
        "startTimestamp": 1791082800,
        "homeTeam": side(1, home),
        "awayTeam": side(2, away),
    }


class FakeProvider:
    """Serves canned fixtures and near-events responses, recording which endpoints were hit."""

    def __init__(self, fixtures: list | Exception, near_events: _NearEventsResponse | Exception):
        self._fixtures = fixtures
        self._near_events = near_events
        self.calls: list[str] = []

    def get_team_fixtures(self, team_id: int, page: int = 0) -> _EventsResponse:
        self.calls.append("fixtures")
        if isinstance(self._fixtures, Exception):
            raise self._fixtures
        return _EventsResponse(events=self._fixtures)

    def get_team_near_events(self, team_id: int) -> _NearEventsResponse:
        self.calls.append("near-events")
        if isinstance(self._near_events, Exception):
            raise self._near_events
        return self._near_events


def test_near_events_payload_parses_both_neighbours():
    parsed = _NearEventsResponse.model_validate({
        "previousEvent": raw_event(17190001, "Renata Zarazua", "Aryna Sabalenka"),
        "nextEvent": raw_event(17214062, "Nikola Bartunkova", "Aryna Sabalenka"),
    })
    assert parsed.previous_event.id == 17190001
    assert parsed.next_event.id == 17214062


def test_near_events_payload_without_a_next_event():
    parsed = _NearEventsResponse.model_validate({
        "previousEvent": raw_event(17190001, "Renata Zarazua", "Aryna Sabalenka"),
    })
    assert parsed.next_event is None


def test_athlete_falls_back_to_the_next_event_when_fixtures_404():
    sabalenka = tennis_player()
    upcoming = match(17214062, home=tennis_player(348987, "Nikola Bartunkova"), away=sabalenka)
    provider = FakeProvider(ProviderNotFoundError("404"), _NearEventsResponse(next_event=upcoming))

    fixtures = Athlete(sabalenka, provider).get_fixtures()

    assert [e.id for e in fixtures] == [Event(upcoming, provider).id]
    assert provider.calls == ["fixtures", "near-events"]


def test_athlete_with_listed_fixtures_makes_no_fallback_request():
    provider = FakeProvider([match(1), match(2)], AssertionError("near-events must not be called"))

    fixtures = Athlete(tennis_player(), provider).get_fixtures()

    assert len(fixtures) == 2
    assert provider.calls == ["fixtures"]


def test_team_fixtures_come_from_the_fixtures_list_alone():
    provider = FakeProvider([match(1), match(2)], AssertionError("near-events must not be called"))

    fixtures = Team(team(1644, "Paris Saint-Germain"), provider).get_fixtures()

    assert len(fixtures) == 2
    assert provider.calls == ["fixtures"]


def test_team_with_no_fixtures_makes_no_fallback_request():
    provider = FakeProvider(ProviderNotFoundError("404"), AssertionError("near-events must not be called"))

    assert len(Team(team(1644, "Paris Saint-Germain"), provider).get_fixtures()) == 0
    assert provider.calls == ["fixtures"]


def test_nothing_scheduled_yields_an_empty_collection():
    provider = FakeProvider(ProviderNotFoundError("404"), _NearEventsResponse(previous_event=match(1)))
    assert len(Athlete(tennis_player(), provider).get_fixtures()) == 0


def test_near_events_404_yields_an_empty_collection():
    provider = FakeProvider(ProviderNotFoundError("404"), ProviderNotFoundError("404"))
    assert len(Athlete(tennis_player(), provider).get_fixtures()) == 0


def test_near_events_fetch_failure_yields_an_empty_collection():
    provider = FakeProvider(ProviderNotFoundError("404"), FetchError("boom"))
    assert len(Athlete(tennis_player(), provider).get_fixtures()) == 0
