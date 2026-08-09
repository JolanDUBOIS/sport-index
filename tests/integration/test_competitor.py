import logging

from sportindex import Athlete, Competitor, Team
from sportindex.api_client import SofascoreProvider

logger = logging.getLogger(__name__)

def test_competitor(provider: SofascoreProvider):
    """Test that the Competitor entity behaves correctly."""
    logger.info("Testing Competitor entity...")

    # Team
    psg = Competitor.from_id("t-cpt:1644", provider)
    assert isinstance(psg, Competitor)
    psg = psg.resolve()
    assert isinstance(psg, Team)
    assert psg.id == "team:1644"
    assert psg.name == "Paris Saint-Germain"
    assert psg.slug == "paris-saint-germain"
    assert psg.short_name == "PSG"
    assert psg.full_name == "Paris Saint-Germain"
    assert psg.name_code == "PSG"
    assert psg.gender.value == "M"
    assert psg.sport.id == "spt:1"
    assert psg.country.alpha3 == "FRA"
    assert len(psg.players) > 0
    assert any(player.id == "p-ath:818244" for player in psg.players)
    assert psg.manager.id == "mng:129465"
    assert psg.venue.id == "vnu:843"

    # Athlete
    lewis_hamilton = Competitor.from_id("t-cpt:7135", provider)
    assert isinstance(lewis_hamilton, Competitor)
    lewis_hamilton = lewis_hamilton.resolve()
    assert isinstance(lewis_hamilton, Athlete)
    assert lewis_hamilton.id == "t-ath:7135"
    assert lewis_hamilton.name == "Lewis Hamilton"
    assert lewis_hamilton.slug == "hamilton-lewis"
    assert lewis_hamilton.first_name == "Lewis"
    assert lewis_hamilton.last_name == "Hamilton"
    assert lewis_hamilton.sport.id == "spt:11"
    assert lewis_hamilton.country.alpha3 == "GBR"
    assert isinstance(lewis_hamilton.parent, Team)
    assert "Ferrari" in lewis_hamilton.parent.name
    assert lewis_hamilton.info is not None
