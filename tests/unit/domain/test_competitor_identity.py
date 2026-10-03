"""A competitor has one class and one ID however it is reached.

Classification reads the provider's `type` on the payload, so it needs no request.
"""

from __future__ import annotations

import pytest

from sportindex.api_client.models import _PlayerData, _TeamData, _TeamResponse
from sportindex.domain import Athlete, Competitor, Team

from factories import player, team


class FakeProvider:
    """Serves full team and player records by raw ID."""

    def __init__(self, *records: _TeamData | _PlayerData) -> None:
        self._teams = {r.id: r for r in records if isinstance(r, _TeamData)}
        self._players = {r.id: r for r in records if isinstance(r, _PlayerData)}

    def get_team(self, team_id: int) -> _TeamResponse:
        return _TeamResponse(team=self._teams[team_id])

    def get_player(self, player_id: int) -> _PlayerData:
        return self._players[player_id]


def sabalenka() -> _TeamData:
    return team(157754, "Aryna Sabalenka", type=1)


def test_the_same_athlete_is_equal_however_it_is_reached(offline):
    as_match_side = Competitor(sabalenka(), offline)
    as_athlete = Athlete(sabalenka(), offline)
    assert as_match_side == as_athlete
    assert as_match_side.id == as_athlete.id == "t-ath:157754"


def test_the_same_team_is_equal_however_it_is_reached(offline):
    assert Competitor(team(1644, "PSG", type=0), offline) == Team(team(1644, "PSG", type=0), offline)


def test_resolve_returns_the_competitor_itself(offline):
    competitor = Competitor(sabalenka(), offline)
    assert competitor.resolve() is competitor


def test_a_team_refuses_a_person(offline):
    with pytest.raises(ValueError, match="describes an athlete"):
        Team(sabalenka(), offline)


def test_an_athlete_refuses_a_team(offline):
    with pytest.raises(ValueError, match="describes a team"):
        Athlete(team(1644, "PSG", type=0), offline)


@pytest.mark.parametrize("entity_id,expected_cls", [
    ("team:1644", Team),
    ("t-ath:157754", Athlete),
    ("p-ath:826643", Athlete),
])
def test_loading_by_id_gives_the_class_the_id_names(entity_id, expected_cls):
    provider = FakeProvider(team(1644, "PSG", type=0), sabalenka(), player(826643, "Kylian Mbappé"))

    competitor = Competitor.from_id(entity_id, provider)

    assert isinstance(competitor, expected_cls)
    assert competitor.id == entity_id


@pytest.mark.parametrize("dropped_id", ["t-cpt:1644", "p-cpt:826643"])
def test_the_undetermined_competitor_ids_no_longer_exist(dropped_id):
    with pytest.raises(ValueError, match="No subclass found"):
        Competitor.resolve_class(dropped_id)
