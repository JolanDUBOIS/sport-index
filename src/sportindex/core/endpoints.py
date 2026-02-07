BASE_URL = "https://www.sofascore.com"
BASE_API_URL = f"{BASE_URL}/api/v1"


ENDPOINTS = {
    # ------------------------------------------------------------------
    # Categories
    # ------------------------------------------------------------------
    "all-categories": f"{BASE_API_URL}/sport/{{sport}}/categories",
    "category-competitions": f"{BASE_API_URL}/category/{{category_id}}/unique-tournaments",

    # ------------------------------------------------------------------
    # Competitions
    # ------------------------------------------------------------------
    "competition": f"{BASE_API_URL}/unique-tournament/{{competition_id}}",
    "competition-standings": f"{BASE_API_URL}/unique-tournament/{{competition_id}}/season/{{season_id}}/standings/{{view}}",
    "competition-fixtures": f"{BASE_API_URL}/unique-tournament/{{competition_id}}/season/{{season_id}}/events/next/{{page}}",
    "competition-results": f"{BASE_API_URL}/unique-tournament/{{competition_id}}/season/{{season_id}}/events/last/{{page}}",
    "competition-seasons": f"{BASE_API_URL}/unique-tournament/{{competition_id}}/seasons",

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
    "lineups": f"{BASE_API_URL}/event/{{event_id}}/lineups",
    "h2h-history": f"{BASE_API_URL}/event/{{event_custom_id}}/h2h/events",

    # ------------------------------------------------------------------
    # Rankings
    # ------------------------------------------------------------------
    "ranking": f"{BASE_API_URL}/rankings/{{ranking_id}}",

    # ------------------------------------------------------------------
    # Search (cross-sport)
    # ------------------------------------------------------------------
    "search-competitions": f"{BASE_API_URL}/search/unique-tournaments",
    "search-teams": f"{BASE_API_URL}/search/teams",
    "search-events": f"{BASE_API_URL}/search/events",
    "search-players": f"{BASE_API_URL}/search/players",
    "search-managers": f"{BASE_API_URL}/search/managers",
    "search-referees": f"{BASE_API_URL}/search/referees",
    "search-venues": f"{BASE_API_URL}/search/venues",
}



### NOTES

# # ------------------------------------------------------------------
# # Motorsport
# # ------------------------------------------------------------------
# "stage-standings-competitor": f"{BASE_API_URL}/stage/{{stage_id}}/standings/competitor",
# "stage-standings-team": f"{BASE_API_URL}/stage/{{stage_id}}/standings/team",
# "stage-extended": f"{BASE_API_URL}/stage/{{stage_id}}/extended",
# "stage-substages": f"{BASE_API_URL}/stage/{{stage_id}}/substages",
# "stage-seasons": f"{BASE_API_URL}/unique-stage/{{stage_id}}/seasons",
# "motorsport-schedule": f"{BASE_API_URL}/stage/sport/motorsport/scheduled/{{date}}",



# Ranking ids:
# 1 - UEFA country rankings
# 2 - FIFA country rankings
# 3 - Rugby union rankings
# 4 - Rugby league rankings
# 5 - ATP player rankings
# 6 - WTA player rankings
# 7 - Live ATP player rankings (not sure what it is)
# 8 - Live WTA player rankings (not sure what it is)
# 9 - UEFA club rankings
# 10 - Doesn't exists
# 11 -> 18 - MMA men rankings (various weight classes)
# 19 -> 22 - MMA women rankings (various weight classes) - 22 is featherweight, less contested (limited rosters)
# 34 - UTR men rankings
# 35 - UTR women rankings
