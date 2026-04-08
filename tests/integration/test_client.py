import pytest

import sportindex
from sportindex import SportClient


@pytest.fixture
def client() -> SportClient:
    return SportClient()


def test_client_cache(client: SportClient):
    """Test that the client handles caching correctly."""
    pass


def test_client_get(client: SportClient):
    """Test that the client can get identifiable entities from the API."""
    # Sport
    football = client.get(sportindex.Sport, 1)
    assert football.id == 1
    assert football.name == "Football"


    # Country
    france = client.get(sportindex.Country, 250)
    assert france.id == 250
    assert france.name == "France"


    # Category
    england_football_cat = client.get(sportindex.Category, 1)
    assert england_football_cat.id == 1
    assert england_football_cat.name == "England"

    challenger_tennis_cat = client.get(sportindex.Category, 72)
    assert challenger_tennis_cat.id == 72
    assert challenger_tennis_cat.name == "Challenger"


    # Channel
    canal_plus = client.get(sportindex.Channel, 287)
    assert canal_plus.id == 287
    assert "Canal+" in canal_plus.name

    bein_sport = client.get(sportindex.Channel, 42)
    assert bein_sport.id == 42
    assert "beIN" in bein_sport.name


    # Competition
    ucl = client.get(sportindex.Competition, 14)
    assert ucl.id == 14
    assert ucl.name == "UEFA Champions League"

    f1 = client.get(sportindex.Competition, 81)
    assert f1.id == 81
    assert f1.name == "Formula 1"


    # Season
    ucl_2425 = client.get(sportindex.Season, 281475211653324)
    assert ucl_2425.id == 281475211653324
    assert ucl_2425.name == "UEFA Champions League 24/25"

    f1_2026 = client.get(sportindex.Season, 562951312589948)
    assert f1_2026.id == 562951312589948
    assert f1_2026.name == "Formula 1 2026"


    # Event
    psg_chelsea = client.get(sportindex.Event, 31262682)
    assert psg_chelsea.id == 31262682
    assert psg_chelsea.name == "Paris Saint Germain Chelsea"

    psg_chelsea = client.get(sportindex.MatchEvent, 31262682)
    assert psg_chelsea.id == 31262682
    assert psg_chelsea.name == "Paris Saint Germain Chelsea"

    japan_gp = client.get(sportindex.Event, 428311)
    assert japan_gp.id == 428311
    assert japan_gp.name == "Japan GP"

    japan_gp = client.get(sportindex.StageEvent, 428311)
    assert japan_gp.id == 428311
    assert japan_gp.name == "Japan GP"


    # Competitor
    psg = client.get(sportindex.Competitor, 3288)
    assert psg.id == 3288
    assert psg.name == "Paris Saint-Germain"

    psg = client.get(sportindex.Team, 3288)
    assert psg.id == 3288
    assert psg.name == "Paris Saint-Germain"

    lewis_hamilton = client.get(sportindex.Competitor, 14270)
    assert lewis_hamilton.id == 14270
    assert lewis_hamilton.name == "Lewis Hamilton"

    lewis_hamilton = client.get(sportindex.Player, 14270)
    assert lewis_hamilton.id == 14270
    assert lewis_hamilton.name == "Lewis Hamilton"

    ousman_dembele = client.get(sportindex.Competitor, 1636489)
    assert ousman_dembele.id == 1636489
    assert ousman_dembele.name == "Ousmane Dembélé"

    ousman_dembele = client.get(sportindex.Player, 1636489)
    assert ousman_dembele.id == 1636489
    assert ousman_dembele.name == "Ousmane Dembélé"


    # Manager
    luis_enrique = client.get(sportindex.Manager, 129465)
    assert luis_enrique.id == 129465
    assert luis_enrique.name == "Luis Enrique"


    # Referee
    szymon_marciniak = client.get(sportindex.Referee, 72926)
    assert szymon_marciniak.id == 72926
    assert szymon_marciniak.name == "Szymon Marciniak"


    # Venue
    parc_des_princes = client.get(sportindex.Venue, 1686)
    assert parc_des_princes.id == 1686
    assert parc_des_princes.name == "Parc des Princes"


def test_client_search(client: SportClient):
    """Test that the client can search searchable entities from the API."""
    pass


def test_client_list(client: SportClient):
    """Test that the client can list listable entities from the API."""
    pass
