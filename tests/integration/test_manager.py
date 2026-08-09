import logging

import sportindex
from sportindex import Manager
from sportindex.api_client import SofascoreProvider

logger = logging.getLogger(__name__)

def test_manager(provider: SofascoreProvider):
    """Test that the Manager entity behaves correctly."""
    logger.info("Testing Manager entity...")

    manager = Manager.from_id("mng:129465", provider)
    assert manager.id == "mng:129465"
    assert manager.name == "Luis Enrique"
    assert manager.slug == "luis-enrique"
    assert manager.short_name == "L. Enrique"
    assert manager.sport.id == "spt:1"
    assert manager.country.alpha3 == "ESP"
    assert manager.team.id == "t-cpt:1644"
    assert len(manager.performances) > 0
    assert all(isinstance(perf, sportindex.ManagerTenure) for perf in manager.performances)
    assert len(manager.get_fixtures()) == 0
    assert all(isinstance(event, sportindex.MatchEvent) for event in manager.get_results())
