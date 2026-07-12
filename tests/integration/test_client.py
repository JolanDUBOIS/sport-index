import pytest

import sportindex
from sportindex import SportClient
from sportindex.exceptions import EntityNotFoundError


def test_client_cache(client: SportClient):
    """Test that the client handles caching correctly."""
    # Get an entity to populate the cache
    football = client.get(sportindex.Sport, "spt:1")
    assert football.id == "spt:1"
    assert football.name == "Football"

    # Get the same entity again and ensure it comes from the cache
    football_cached = client.get(sportindex.Sport, "spt:1")
    assert football_cached is football


def test_client_get(client: SportClient):
    """Test that the client can get identifiable entities from the API."""
    # Sport
    football = client.get(sportindex.Sport, "spt:1")
    assert football.id == "spt:1"
    assert football.name == "Football"

    # Country
    france = client.get(sportindex.Country, "ctr:250")
    assert france.id == "ctr:250"
    assert france.name == "France"

    # Category
    england_football_cat = client.get(sportindex.Category, "cat:1")
    assert england_football_cat.id == "cat:1"
    assert england_football_cat.name == "England"

    challenger_tennis_cat = client.get(sportindex.Category, "cat:72")
    assert challenger_tennis_cat.id == "cat:72"
    assert challenger_tennis_cat.name == "Challenger"

    # Channel
    canal_plus = client.get(sportindex.Channel, "chl:287")
    assert canal_plus.id == "chl:287"
    assert "Canal+" in canal_plus.name

    bein_sport = client.get(sportindex.Channel, "chl:42")
    assert bein_sport.id == "chl:42"
    assert "beIN" in bein_sport.name

    # Competition
    ucl = client.get(sportindex.Competition, "trnc:7")
    assert ucl.id == "trnc:7"
    assert ucl.name == "UEFA Champions League"

    f1 = client.get(sportindex.Competition, "stgc:40")
    assert f1.id == "stgc:40"
    assert f1.name == "Formula 1"

    # Season
    ucl_2425 = client.get(sportindex.Season, "trnc:7:trns:61644")
    assert ucl_2425.id == "trnc:7:trns:61644"
    assert ucl_2425.name == "UEFA Champions League 24/25"

    f1_2026 = client.get(sportindex.Season, "stgc:40:stgs:214140")
    assert f1_2026.id == "stgc:40:stgs:214140"
    assert f1_2026.name == "Formula 1 2026"

    # Event
    psg_chelsea = client.get(sportindex.Event, "mch:15631341")
    assert psg_chelsea.id == "mch:15631341"
    assert psg_chelsea.name == "Paris Saint Germain Chelsea"
    assert isinstance(psg_chelsea, sportindex.MatchEvent)

    psg_chelsea = client.get(sportindex.MatchEvent, "mch:15631341")
    assert psg_chelsea.id == "mch:15631341"
    assert psg_chelsea.name == "Paris Saint Germain Chelsea"
    assert isinstance(psg_chelsea, sportindex.MatchEvent)

    japan_gp = client.get(sportindex.Event, "stg:214155")
    assert japan_gp.id == "stg:214155"
    assert japan_gp.name == "Japan GP"
    assert isinstance(japan_gp, sportindex.StageEvent)

    japan_gp = client.get(sportindex.StageEvent, "stg:214155")
    assert japan_gp.id == "stg:214155"
    assert japan_gp.name == "Japan GP"
    assert isinstance(japan_gp, sportindex.StageEvent)

    # Competitor
    psg = client.get(sportindex.Competitor, "team:1644")
    assert psg.id == "team:1644"
    assert psg.name == "Paris Saint-Germain"
    assert isinstance(psg, sportindex.Competitor)
    psg = psg.resolve()
    assert isinstance(psg, sportindex.Team)

    psg = client.get(sportindex.Team, "team:1644")
    assert psg.id == "team:1644"
    assert psg.name == "Paris Saint-Germain"
    assert isinstance(psg, sportindex.Team)

    lewis_hamilton = client.get(sportindex.Competitor, "t-ath:7135")
    assert lewis_hamilton.id == "t-ath:7135"
    assert lewis_hamilton.name == "Lewis Hamilton"
    assert isinstance(lewis_hamilton, sportindex.Competitor)
    lewis_hamilton = lewis_hamilton.resolve()
    assert isinstance(lewis_hamilton, sportindex.Athlete)

    lewis_hamilton = client.get(sportindex.Athlete, "t-ath:7135")
    assert lewis_hamilton.id == "t-ath:7135"
    assert lewis_hamilton.name == "Lewis Hamilton"
    assert isinstance(lewis_hamilton, sportindex.Athlete)

    ousman_dembele = client.get(sportindex.Competitor, "p-ath:818244")
    assert ousman_dembele.id == "p-ath:818244"
    assert ousman_dembele.name == "Ousmane Dembélé"
    assert isinstance(ousman_dembele, sportindex.Competitor)
    ousman_dembele = ousman_dembele.resolve()
    assert isinstance(ousman_dembele, sportindex.Athlete)

    ousman_dembele = client.get(sportindex.Athlete, "p-ath:818244")
    assert ousman_dembele.id == "p-ath:818244"
    assert ousman_dembele.name == "Ousmane Dembélé"
    assert isinstance(ousman_dembele, sportindex.Athlete)

    # Manager
    luis_enrique = client.get(sportindex.Manager, "mng:129465")
    assert luis_enrique.id == "mng:129465"
    assert luis_enrique.name == "Luis Enrique"

    # Referee
    szymon_marciniak = client.get(sportindex.Referee, "ref:72926")
    assert szymon_marciniak.id == "ref:72926"
    assert szymon_marciniak.name == "Szymon Marciniak"

    # Venue
    parc_des_princes = client.get(sportindex.Venue, "vnu:843")
    assert parc_des_princes.id == "vnu:843"
    assert parc_des_princes.name == "Parc des Princes"

    # TODO - Add a test for _StageVenue


def test_client_search(client: SportClient):
    """Test that the client can search searchable entities from the API."""
    # Competition
    ucl_search = client.search(sportindex.Competition, "UEFA Champions League")
    assert len(ucl_search) > 0
    assert any(comp.id == "trnc:7" for comp in ucl_search)

    f1_search = client.search(sportindex.Competition, "Formula 1")
    assert len(f1_search) > 0
    assert any(comp.id == "stgc:40" for comp in f1_search)

    # Competitor
    psg_search = client.search(sportindex.Competitor, "Paris Saint-Germain")
    assert len(psg_search) > 0
    assert any(comp.id == "team:1644" for comp in psg_search)
    assert isinstance(psg_search.get(id="team:1644"), sportindex.Competitor)

    psg_search_2 = client.search(sportindex.Team, "PSG")
    assert len(psg_search_2) > 0
    assert any(comp.id == "team:1644" for comp in psg_search_2)
    assert isinstance(psg_search_2.get(id="team:1644"), sportindex.Team)

    lewis_search = client.search(sportindex.Competitor, "Lewis Hamilton")
    assert len(lewis_search) > 0
    assert any(comp.id == "t-ath:7135" for comp in lewis_search)
    assert isinstance(lewis_search.get(id="t-ath:7135"), sportindex.Competitor)

    ousmane_search = client.search(sportindex.Competitor, "Ousmane Dembélé")
    assert len(ousmane_search) > 0
    assert any(comp.id == "p-ath:818244" for comp in ousmane_search)
    assert isinstance(ousmane_search.get(id="p-ath:818244"), sportindex.Competitor)

    # Manager
    luis_enrique_search = client.search(sportindex.Manager, "Luis Enrique")
    assert len(luis_enrique_search) > 0
    assert any(comp.id == "mng:129465" for comp in luis_enrique_search)

    # Referee
    szymon_marciniak_search = client.search(sportindex.Referee, "Szymon Marciniak")
    assert len(szymon_marciniak_search) > 0
    assert any(comp.id == "ref:72926" for comp in szymon_marciniak_search)

    # Venue
    parc_des_princes_search = client.search(sportindex.Venue, "Parc des Princes")
    assert len(parc_des_princes_search) > 0
    assert any(comp.id == "vnu:843" for comp in parc_des_princes_search)


def test_client_list(client: SportClient):
    """Test that the client can list listable entities from the API."""
    # Sport
    sports = client.list(sportindex.Sport)
    assert len(sports) == 22
    assert any(sport.id == "spt:1" and sport.name == "Football" for sport in sports)

    # Country
    countries = client.list(sportindex.Country)
    assert len(countries) > 0
    assert any(country.id == "ctr:250" and country.name == "France" for country in countries)

    # Category
    football_categories = client.list(sportindex.Category, sport_id="spt:1")
    assert len(football_categories) > 0
    assert any(cat.id == "cat:1" and cat.name == "England" for cat in football_categories)

    all_categories = client.list(sportindex.Category)
    assert len(all_categories) > 0
    assert any(cat.id == "cat:1" and cat.name == "England" for cat in all_categories)

    # Channel
    with pytest.raises(NotImplementedError):
        client.list(sportindex.Channel)

    # Competition
    eu_football_comps = client.list(sportindex.Competition, sport_id="spt:1", category_id="cat:1465")
    assert len(eu_football_comps) > 0
    assert any(comp.id == "trnc:7" and comp.name == "UEFA Champions League" for comp in eu_football_comps)

    eu_football_comps = client.list(sportindex.Competition, category_id="cat:1465")
    assert len(eu_football_comps) > 0
    assert any(comp.id == "trnc:7" and comp.name == "UEFA Champions League" for comp in eu_football_comps)

    with pytest.raises(EntityNotFoundError):
        client.list(sportindex.Competition)

    # Season
    ucl_seasons = client.list(sportindex.Season, competition_id="trnc:7")
    assert len(ucl_seasons) > 0
    assert any(season.id == "trnc:7:trns:61644" and season.name == "UEFA Champions League 24/25" for season in ucl_seasons)

    with pytest.raises(EntityNotFoundError):
        client.list(sportindex.Season)

    # Event
    ucl_2425_events = client.list(sportindex.Event, season_id="trnc:7:trns:76953") # UCL 25/26
    assert len(ucl_2425_events) > 0
    assert any(event.id == "mch:15631341" and event.name == "Paris Saint Germain Chelsea" for event in ucl_2425_events)

    with pytest.raises(EntityNotFoundError):
        client.list(sportindex.Event)
