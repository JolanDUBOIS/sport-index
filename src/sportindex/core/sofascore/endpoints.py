BASE_URL = "https://www.sofascore.com"
BASE_API_URL = f"{BASE_URL}/api/v1"


ENDPOINTS = {
    # ------------------------------------------------------------------
    # Categories
    # ------------------------------------------------------------------
    "all-categories": f"{BASE_API_URL}/sport/{{sport}}/categories",
    "category-unique-tournaments": f"{BASE_API_URL}/category/{{category_id}}/unique-tournaments",

    # ------------------------------------------------------------------
    # Unique Tournaments
    # ------------------------------------------------------------------
    "unique-tournament": f"{BASE_API_URL}/unique-tournament/{{unique_tournament_id}}",
    "unique-tournament-standings": f"{BASE_API_URL}/unique-tournament/{{unique_tournament_id}}/season/{{season_id}}/standings/{{view}}",
    "unique-tournament-fixtures": f"{BASE_API_URL}/unique-tournament/{{unique_tournament_id}}/season/{{season_id}}/events/next/{{page}}",
    "unique-tournament-results": f"{BASE_API_URL}/unique-tournament/{{unique_tournament_id}}/season/{{season_id}}/events/last/{{page}}",
    "unique-tournament-seasons": f"{BASE_API_URL}/unique-tournament/{{unique_tournament_id}}/seasons",
    # ------------------------------------------------------------------
    # Teams / Players / Managers / Referees
    # ------------------------------------------------------------------
    "team": f"{BASE_API_URL}/team/{{team_id}}",
    "team-fixtures": f"{BASE_API_URL}/team/{{team_id}}/events/next/{{page}}",
    "team-results": f"{BASE_API_URL}/team/{{team_id}}/events/last/{{page}}",
    "team-players": f"{BASE_API_URL}/team/{{team_id}}/players",
    "team-seasons": f"{BASE_API_URL}/team/{{team_id}}/team-statistics/seasons",
    "team-year-stats": f"{BASE_API_URL}/team/{{team_id}}/year-statistics/{{year}}",

    "player": f"{BASE_API_URL}/player/{{player_id}}",
    "player-results": f"{BASE_API_URL}/player/{{player_id}}/events/last/{{page}}",
    "player-seasons": f"{BASE_API_URL}/player/{{player_id}}/statistics/seasons",

    "manager": f"{BASE_API_URL}/manager/{{manager_id}}",
    "manager-results": f"{BASE_API_URL}/manager/{{manager_id}}/events/last/{{page}}",
    "manager-seasons": f"{BASE_API_URL}/manager/{{manager_id}}/statistics/seasons",

    "referee": f"{BASE_API_URL}/referee/{{referee_id}}",
    "referee-results": f"{BASE_API_URL}/referee/{{referee_id}}/events/last/{{page}}",

    # ------------------------------------------------------------------
    # Venues
    # ------------------------------------------------------------------
    "venue": f"{BASE_API_URL}/venue/{{venue_id}}",
    "venue-fixtures": f"{BASE_API_URL}/venue/{{venue_id}}/events/all/next/{{page}}",
    "venue-results": f"{BASE_API_URL}/venue/{{venue_id}}/events/all/last/{{page}}",

    # ------------------------------------------------------------------
    # Events / Matches
    # ------------------------------------------------------------------
    "event": f"{BASE_API_URL}/event/{{event_id}}",
    "event-lineups": f"{BASE_API_URL}/event/{{event_id}}/lineups",
    "event-incidents": f"{BASE_API_URL}/event/{{event_id}}/incidents",
    "event-statistics": f"{BASE_API_URL}/event/{{event_id}}/statistics",
    "event-graph": f"{BASE_API_URL}/event/{{event_id}}/graph",
    "event-channels": f"{BASE_API_URL}/tv/event/{{event_id}}/country-channels",
    "event-h2h-history": f"{BASE_API_URL}/event/{{event_custom_id}}/h2h/events",
    "scheduled-events": f"{BASE_API_URL}/sport/{{sport}}/scheduled-events/{{date}}",

    # ------------------------------------------------------------------
    # Rankings
    # ------------------------------------------------------------------
    "ranking": f"{BASE_API_URL}/rankings/{{ranking_id}}",

    # ------------------------------------------------------------------
    # Motorsport
    # ------------------------------------------------------------------
    "unique-stage-seasons": f"{BASE_API_URL}/unique-stage/{{unique_stage_id}}/seasons",
    "stage": f"{BASE_API_URL}/stage/{{stage_id}}",
    "substages": f"{BASE_API_URL}/stage/{{stage_id}}/substages",
    "stage-details": f"{BASE_API_URL}/stage/{{stage_id}}/extended",
    "standings-competitors": f"{BASE_API_URL}/stage/{{stage_id}}/standings/competitor",
    "standings-teams": f"{BASE_API_URL}/stage/{{stage_id}}/standings/team",

    # ------------------------------------------------------------------
    # TV Channels
    # ------------------------------------------------------------------
    "country-channels": f"{BASE_API_URL}/tv/country/{{country_code}}/channels",
    "channel-schedule": f"{BASE_API_URL}/tv/channel/{{channel_id}}/schedule",
    "country-popular-channels": f"{BASE_API_URL}/tv/country/{{country_code}}/popular-channels", # Not added to provider, doesn't seem useful
    "channel-event-votes": f"{BASE_API_URL}/tv/channel/{{channel_id}}/event/{{event_id}}/votes", # Not added to provider, doesn't seem useful

    # ------------------------------------------------------------------
    # Search (cross-sport)
    # ------------------------------------------------------------------
    "search-unique-tournaments": f"{BASE_API_URL}/search/unique-tournaments",
    "search-teams": f"{BASE_API_URL}/search/teams",
    "search-events": f"{BASE_API_URL}/search/events",
    "search-players": f"{BASE_API_URL}/search/players",
    "search-managers": f"{BASE_API_URL}/search/managers",
    "search-referees": f"{BASE_API_URL}/search/referees",
    "search-venues": f"{BASE_API_URL}/search/venues",
}
