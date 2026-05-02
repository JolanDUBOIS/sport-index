BASE_URL = "https://www.sofascore.com/sitemaps"

country_code = "en" # TODO - Should we adapt this depending on user's location ? Should we ask for user preferred language or smthg like that ?

ENDPOINTS = {
    # "events": f"{BASE_URL}/en_sitemap_events_index.xml.gz",
    # "main": f"{BASE_URL}/{country_code}_sitemap_main_index.xml.gz",
    "managers": f"{BASE_URL}/en_sitemap_managers.xml.gz",
    "players": f"{BASE_URL}/en_sitemap_players_{{sport_slug}}.xml.gz",
    # "player_comparison": f"{BASE_URL}/en_sitemap_player_comparison.xml.gz",
    "races": f"{BASE_URL}/en_sitemap_races.xml.gz",
    # "sports": f"{BASE_URL}/en_sitemap_sports.xml.gz",
    "teams": f"{BASE_URL}/en_sitemap_teams_{{sport_slug}}.xml.gz",
    "tournaments": f"{BASE_URL}/en_sitemap_tournaments_{{sport_slug}}.xml.gz",
    "venues": f"{BASE_URL}/en_sitemap_venues.xml.gz",
}
