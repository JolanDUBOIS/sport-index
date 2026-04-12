from datetime import datetime

from sportindex import Competition, Season, SportContestNature
from sportindex.provider import SofascoreProvider


def test_competition(provider: SofascoreProvider):
    """Test that the Competition entity behaves correctly."""
    ucl = Competition.from_id(14, provider)
    assert ucl.id == 14
    assert ucl.slug == "uefa-champions-league"
    assert ucl.name == "UEFA Champions League"
    assert ucl.sport.id == 1
    assert ucl.sport_nature == SportContestNature.OPPOSITION
    assert ucl.sport_nature == ucl.sport.nature
    assert ucl.category.id == 1465
    assert len(ucl.seasons) > 0


def test_season(provider: SofascoreProvider):
    """Test that the Season entity behaves correctly."""
    ucl_24_25 = Season.from_id(281475211653324, provider)
    assert ucl_24_25.id == 281475211653324
    assert ucl_24_25.name == "UEFA Champions League 24/25"
    assert ucl_24_25.year == "24/25"
    assert isinstance(ucl_24_25.start, datetime) or ucl_24_25.start is None
    assert ucl_24_25.sport.id == 1
    assert ucl_24_25.sport_nature == SportContestNature.OPPOSITION
    assert ucl_24_25.competition.id == 14
    assert ucl_24_25.current_round.name == "Final"
    assert len(ucl_24_25.rounds) > 0
    assert len(ucl_24_25.standings) > 0

    fixtures = ucl_24_25.get_fixtures()
    assert len(fixtures) == 0
    results = ucl_24_25.get_results()
    assert len(results) > 0
