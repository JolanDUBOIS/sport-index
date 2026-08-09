"""Offline unit tests for domain fallbacks on incomplete provider payloads.

These cover the cases where a payload field the domain layer reads is optional,
and the entity has to fall back to something else rather than fail.
"""

import pytest

from sportindex.api_client.models import (
    Score,
    _CountryData,
    _EventData,
    _ManagerData,
    _SportData,
    _TeamData,
)
from sportindex.domain import Competitor, Country, Event, Manager

FOOTBALL = _SportData(id=1, name="Football", slug="football")


def _raw_event(display_score: object) -> _EventData:
    """Build an _EventData the way the provider does — from a raw API payload."""
    team = {"id": 1, "slug": "team", "name": "Team", "sport": FOOTBALL.model_dump()}
    return _EventData.model_validate({
        "id": 1,
        "customId": "abc",
        "slug": "home-away",
        "startTimestamp": 1700000000,
        "homeTeam": team,
        "awayTeam": team,
        "homeScore": {"display": display_score},
        "awayScore": {"display": display_score},
    })


class TestCountryNameFallbacks:
    """Country.name and .slug are read from the payload, where both are optional."""

    def test_name_falls_back_when_payload_has_only_an_alpha_code(self):
        country = Country(_CountryData(alpha2="FR"), None)
        assert country.name == "France"
        assert country.slug == "france"

    def test_name_falls_back_to_the_slug_when_payload_has_no_name(self):
        country = Country(_CountryData(slug="united-states"), None)
        assert country.name == "United States"
        assert country.slug == "united-states"

    def test_unresolvable_payload_raises_rather_than_crashing_on_the_missing_name(self):
        with pytest.raises(ValueError):
            Country(_CountryData(), None)


class TestMatchEventScore:
    """MatchEvent.score is built from a display field the provider may render non-numerically."""

    def test_numeric_score_is_parsed(self):
        assert _raw_event(2).id is not None
        assert Event(_raw_event(2), None).score == Score(home=2, away=2)

    def test_non_numeric_score_is_none_rather_than_raising(self):
        assert Event(_raw_event("AD"), None).score is None

    def test_absent_score_is_none(self):
        assert Event(_raw_event(None), None).score is None


class TestShortNameFallbacks:
    """short_name is optional on every payload that carries it."""

    def test_competitor_short_name_falls_back_to_name(self):
        team = _TeamData(id=1, slug="psg", name="Paris Saint-Germain", sport=FOOTBALL)
        assert Competitor(team, None).short_name == "Paris Saint-Germain"

    def test_competitor_short_name_is_used_when_present(self):
        team = _TeamData(id=1, slug="psg", name="Paris Saint-Germain", shortName="PSG", sport=FOOTBALL)
        assert Competitor(team, None).short_name == "PSG"

    def test_manager_short_name_falls_back_to_name(self):
        assert Manager(_ManagerData(id=1, slug="zz", name="Zinedine Zidane"), None).short_name == "Zinedine Zidane"

    def test_manager_short_name_is_used_when_present(self):
        manager = _ManagerData(id=1, slug="zz", name="Zinedine Zidane", shortName="Z. Zidane")
        assert Manager(manager, None).short_name == "Z. Zidane"
