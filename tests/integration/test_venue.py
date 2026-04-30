import logging

import sportindex
from sportindex import Venue
from sportindex.api_client import SofascoreProvider

logger = logging.getLogger(__name__)

def test_venue(provider: SofascoreProvider):
    """Test that the Venue entity behaves correctly."""
    logger.info("Testing Venue entity...")

    # Parc des Princes - Paris Saint-Germain home stadium
    parc_des_princes = Venue.from_id(1686, provider)
    assert parc_des_princes.id == 1686
    assert parc_des_princes.name == "Parc des Princes"
    assert parc_des_princes.city == "Paris"
    assert parc_des_princes.capacity >= 47000 and parc_des_princes.capacity <= 49000
    assert parc_des_princes.country.alpha3 == "FRA"
    assert len(parc_des_princes.teams) == 1
    assert parc_des_princes.teams[0].id == 3288
    assert len(parc_des_princes.get_fixtures()) > 0, "Could be 0 if no upcoming fixtures, if so, please check the provider data"
    assert all(isinstance(event, sportindex.MatchEvent) for event in parc_des_princes.get_fixtures())
    assert len(parc_des_princes.get_results()) > 0, "Could be 0 if no recent results, if so, please check the provider data"
    assert all(isinstance(event, sportindex.MatchEvent) for event in parc_des_princes.get_results())

    # Formula 1 - Japan GP at Suzuka Circuit
    japan_gp_venue = Venue.from_id(428311, provider)
    assert japan_gp_venue.id == 428311
    assert japan_gp_venue.name == "Suzuka"
    assert japan_gp_venue.city == "Suzuka"
    assert japan_gp_venue.capacity is None
    assert japan_gp_venue.country.alpha3 == "JPN"
    assert len(japan_gp_venue.teams) == 0
    assert len(japan_gp_venue.get_fixtures()) == 0
    assert len(japan_gp_venue.get_results()) == 0
