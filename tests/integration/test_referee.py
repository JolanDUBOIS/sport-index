import logging

import sportindex
from sportindex import Referee
from sportindex.api_client import SofascoreProvider

logger = logging.getLogger(__name__)

def test_referee(provider: SofascoreProvider):
    """Test that the Referee entity behaves correctly."""
    logger.info("Testing Referee entity...")

    szymon_marciniak = Referee.from_id("ref:72926", provider)
    assert szymon_marciniak.id == "ref:72926"
    assert szymon_marciniak.name == "Szymon Marciniak"
    assert szymon_marciniak.slug == "marciniak-szymon"
    assert szymon_marciniak.sport.id == "spt:1"
    assert szymon_marciniak.country.alpha3 == "POL"
    assert szymon_marciniak.games > 50
    assert isinstance(szymon_marciniak.cards, sportindex.Cards)
    assert szymon_marciniak.cards.yellow > 10
    assert len(szymon_marciniak.get_fixtures()) == 0
    assert all(isinstance(event, sportindex.MatchEvent) for event in szymon_marciniak.get_results())
