from datetime import datetime

from sportindex import Competition, Season
from sportindex.api_client import SofascoreProvider


def test_competition(provider: SofascoreProvider):
    """Test that the Competition entity behaves correctly."""
    ucl = Competition.from_id("trnc:7", provider)
    assert ucl.id == "trnc:7"
    assert ucl.slug == "uefa-champions-league"
    assert ucl.name == "UEFA Champions League"
    assert ucl.sport.id == "spt:1"
    assert ucl.category.id == "cat:1465"
    assert len(ucl.seasons) > 0


def test_season(provider: SofascoreProvider):
    """Test that the Season entity behaves correctly."""
    ucl_24_25 = Season.from_id("trnc:7:trns:61644", provider)
    assert ucl_24_25.id == "trnc:7:trns:61644"
    assert ucl_24_25.name == "UEFA Champions League 24/25"
    assert ucl_24_25.year == "24/25"
    assert isinstance(ucl_24_25.start, datetime) or ucl_24_25.start is None
    assert ucl_24_25.sport.id == "spt:1"
    assert ucl_24_25.competition.id == "trnc:7"
    assert ucl_24_25.current_round.name == "Final"
    assert len(ucl_24_25.rounds) > 0
    assert len(ucl_24_25.standings) > 0

    fixtures = ucl_24_25.get_fixtures()
    assert len(fixtures) == 0
    results = ucl_24_25.get_results()
    assert len(results) > 0
