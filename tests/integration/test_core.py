import logging

import sportindex
from sportindex import SportClient, Sport, Country, Category, SportContestNature
from sportindex.provider import SofascoreProvider


logger = logging.getLogger(__name__)

def test_sport(provider: SofascoreProvider):
    """Test that the Sport entity behaves correctly."""
    logger.info("Testing Sport entity...")

    # Test all attributes and methods
    football = Sport.from_id(1, provider)
    assert football.id == 1
    assert football.slug == "football"
    assert football.name == "Football"
    assert football.nature == SportContestNature.OPPOSITION

    football_cats = football.categories
    assert len(football_cats) > 0
    assert any(cat.id == 1 and cat.name == "England" for cat in football_cats)

    football_rankings = football.get_rankings()
    assert len(football_rankings) == 3
    assert all(isinstance(ranking, sportindex.Rankings) for ranking in football_rankings)

    all_sports = Sport.all(provider)
    assert football in all_sports
    assert len(all_sports) == 22

    # Test other sports to ensure they also have categories
    basketball = Sport.from_id(2, provider)
    assert len(basketball.categories) > 0
    assert basketball.nature == SportContestNature.OPPOSITION

    motorsport = Sport.from_id(11, provider)
    assert len(motorsport.categories) > 0
    assert motorsport.nature == SportContestNature.COMPARISON

    cycling = Sport.from_id(65, provider)
    assert len(cycling.categories) > 0
    assert cycling.nature == SportContestNature.COMPARISON


def test_country(provider: SofascoreProvider):
    """Test that the Country entity behaves correctly."""
    logger.info("Testing Country entity...")

    france = Country.from_id(250, provider)
    assert france.id == 250
    assert france.name == "France"
    assert france.slug == "france"
    assert france.alpha2 == "FR"
    assert france.alpha3 == "FRA"

    france = Country.from_alpha("FR", provider)
    assert france.id == 250

    france = Country.from_alpha("FRA", provider)
    assert france.id == 250

    france = Country.from_name("France", provider)
    assert france.id == 250

    all_countries = Country.all(provider)
    assert france in all_countries


def test_category(client: SportClient, provider: SofascoreProvider):
    """Test that the Category entity behaves correctly."""
    logger.info("Testing Category entity...")

    football_eu = Category.from_id(1465, provider) # Warning - Category.from_id is expensive (calls the API many times)
    assert football_eu.id == 1465
    assert football_eu.name == "Europe"
    assert football_eu.slug == "europe"
    assert football_eu.sport.id == 1
    assert football_eu.sport_nature == SportContestNature.OPPOSITION
    assert football_eu.country is None
    assert len(football_eu.competitions) > 0 and any(comp.id == 14 and comp.name == "UEFA Champions League" for comp in football_eu.competitions)

    f1_cat = client.get(sportindex.Sport, 11).categories.get(id=36)
    assert f1_cat.id == 36
    assert len(f1_cat.competitions) == 1

    us_basketball_cat = client.get(sportindex.Sport, 2).categories.get(id=15)
    assert us_basketball_cat.id == 15
    assert len(us_basketball_cat.competitions) > 0
    assert us_basketball_cat.country == Country.from_alpha("USA", provider)

    all_cats = Category.all(provider)
    assert football_eu in all_cats
    assert f1_cat in all_cats
    assert us_basketball_cat in all_cats
