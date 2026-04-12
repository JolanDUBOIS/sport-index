import logging

from sportindex import Channel
from sportindex.provider import SofascoreProvider


logger = logging.getLogger(__name__)

def test_channel(provider: SofascoreProvider):
    """Test that the Channel entity behaves correctly."""
    logger.info("Testing Channel entity...")

    canal_plus = Channel.from_id(287, provider)
    assert canal_plus.id == 287
    assert "canal" in canal_plus.name.lower()
    assert len(canal_plus.get_events()) > 0, "Expected Canal+ to have scheduled events, though it is possible it may not at the moment. Check the provider data if this fails."
