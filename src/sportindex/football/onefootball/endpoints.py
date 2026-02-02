BASE_URL = "https://www.onefootball.com"

ENDPOINT_BASE = f"{BASE_URL}/_next/data/{{build_id}}/{{language}}"

ENDPOINTS = {
    "main-page": f"{BASE_URL}/{{language}}/home",
    "all-competitions": f"{ENDPOINT_BASE}/all-competitions/{{letter}}.json?directory-entity=all-competitions&entity-page={{letter}}",
    "competition-standings": f"{ENDPOINT_BASE}/competition/{{competition_id}}/table.json?competition-id={{competition_id}}&entity-page=table",
    "competition-fixtures": f"{ENDPOINT_BASE}/competition/{{competition_id}}/fixtures.json?competition-id={{competition_id}}&entity-page=fixtures",
    "competition-results": f"{ENDPOINT_BASE}/competition/{{competition_id}}/results.json?competition-id={{competition_id}}&entity-page=results",
    "all-teams": f"{ENDPOINT_BASE}/all-teams/{{letter}}.json?page={{page}}&directory-entity=all-teams&entity-page={{letter}}",
    "team-fixtures": f"{ENDPOINT_BASE}/team/{{team_id}}/fixtures.json?team-id={{team_id}}&entity-page=fixtures",
    "team-results": f"{ENDPOINT_BASE}/team/{{team_id}}/results.json?team-id={{team_id}}&entity-page=results",
    "team-players": f"{ENDPOINT_BASE}/team/{{team_id}}/squad.json?team-id={{team_id}}&entity-page=squad",
    "matches": f"{ENDPOINT_BASE}/matches.json?date={{date}}",
    "match-details": f"{ENDPOINT_BASE}/match/{{match_id}}.json?match-id={{match_id}}",
    "player-details": f"{ENDPOINT_BASE}/player/{{player_id}}.json?player-id={{player_id}}",
    "player-stats": f"{ENDPOINT_BASE}/player/{{player_id}}/stats.json?player-id={{player_id}}&player-id=stats&seasonId={{season_id}}",
}
