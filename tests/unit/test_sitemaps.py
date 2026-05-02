import sportindex.sitemaps as sitemaps
from sportindex.sitemaps import SofascoreSitemapProvider


def test_get_managers_list(sitemap_provider: SofascoreSitemapProvider):
    managers = sitemap_provider.get_managers_list()
    assert isinstance(managers, list)
    assert all(isinstance(m, sitemaps._ManagerStub) for m in managers)

    enrique = next((m for m in managers if m.id == 129465), None)
    assert enrique is not None
    assert enrique.slug == "luis-enrique"
    assert enrique.sport_slug == "football"


def test_get_players_list(sitemap_provider: SofascoreSitemapProvider):
    players = sitemap_provider.get_players_list("football")
    assert isinstance(players, list)
    assert all(isinstance(p, sitemaps._PlayerStub) for p in players)

    ousmane = next((p for p in players if p.id == 818244), None)
    assert ousmane is not None
    assert ousmane.slug == "ousmane-dembele"
    assert ousmane.sport_slug == "football"


def test_get_races_list(sitemap_provider: SofascoreSitemapProvider):
    races = sitemap_provider.get_races_list()
    assert isinstance(races, list)
    assert all(isinstance(r, sitemaps._RaceStub) for r in races)

    aus_gp = next((r for r in races if r.id == 214141), None)
    assert aus_gp is not None
    assert aus_gp.slug == "australia-gp"
    assert aus_gp.sport_slug == "motorsport"


def test_get_teams_list(sitemap_provider: SofascoreSitemapProvider):
    teams = sitemap_provider.get_teams_list("football")
    assert isinstance(teams, list)
    assert all(isinstance(t, sitemaps._TeamStub) for t in teams)

    psg = next((t for t in teams if t.id == 1644), None)
    assert psg is not None
    assert psg.slug == "paris-saint-germain"
    assert psg.sport_slug == "football"


def test_get_tournaments_list(sitemap_provider: SofascoreSitemapProvider):
    tournaments = sitemap_provider.get_tournaments_list("football")
    assert isinstance(tournaments, list)
    assert all(isinstance(t, sitemaps._TournamentStub) for t in tournaments)

    wc_2026 = next((t for t in tournaments if t.id == 16), None)
    assert wc_2026 is not None
    assert wc_2026.slug == "world-championship"
    assert wc_2026.sport_slug == "football"
    assert wc_2026.category_slug == "world"


def test_get_venues_list(sitemap_provider: SofascoreSitemapProvider):
    venues = sitemap_provider.get_venues_list()
    assert isinstance(venues, list)
    assert all(isinstance(v, sitemaps._VenueStub) for v in venues)

    parc_des_princes = next((v for v in venues if v.id == 843), None)
    assert parc_des_princes is not None
    assert parc_des_princes.slug == "parc-des-princes"
    assert parc_des_princes.country_slug == "france"
