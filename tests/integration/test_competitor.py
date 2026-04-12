import logging

import sportindex
from sportindex import Competitor, Team, Athlete
from sportindex.provider import SofascoreProvider


logger = logging.getLogger(__name__)

def test_competitor(provider: SofascoreProvider):
    """Test that the Competitor entity behaves correctly."""
    logger.info("Testing Competitor entity...")

    # Team
    psg = Competitor.from_id(3288, provider)
    assert isinstance(psg, Team)
    assert psg.id == 3288
    assert psg.name == "Paris Saint-Germain"
    assert psg.slug == "paris-saint-germain"
    assert psg.short_name == "PSG"
    assert psg.full_name == "Paris Saint-Germain"
    assert psg.name_code == "PSG"
    assert psg.kind == "team"
    assert psg.gender.value == "M"
    assert psg.sport.id == 1
    assert psg.country.alpha3 == "FRA"
    assert len(psg.players) > 0
    assert any(player.id == 1636489 for player in psg.players)
    assert psg.manager.id == 129465
    assert psg.venue.id == 1686

    # Athlete
    lewis_hamilton = Competitor.from_id(14270, provider)
    assert isinstance(lewis_hamilton, Athlete)
    assert lewis_hamilton.id == 14270
    assert lewis_hamilton.name == "Lewis Hamilton"
    assert lewis_hamilton.slug == "hamilton-lewis"
    assert lewis_hamilton.first_name == "Lewis"
    assert lewis_hamilton.last_name == "Hamilton"
    assert lewis_hamilton.kind == "player"
    assert lewis_hamilton.sport.id == 11
    assert lewis_hamilton.country.alpha3 == "GBR"
    assert isinstance(lewis_hamilton.parent, Team)
    assert "Ferrari" in lewis_hamilton.parent.name
    assert lewis_hamilton.info is not None
