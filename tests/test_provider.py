import logging
from contextlib import contextmanager

import pytest

from tests.test_config import TEST_CONFIG
from sportindex.exceptions import ProviderNotFoundError
from sportindex.provider import SofascoreProvider, RecordingFetcher
from sportindex.provider.models import (
    _CategoryData, _UniqueTournamentData, _UniqueStageData, _SeasonData,
    _TeamStandingsData, _EventsResponse, _TeamResponse, _TeamData,
    _UniqueTournamentSeasonsResponse, TeamPlayers, TeamYearSurfaceStats,
    _StageData, RaceResults, DriverCareerHistory, RaceResults, 
    _PlayerData, PlayerSeasonStats, _ManagerData, ManagerTenure,
    _RefereeData, _VenueData, _EventData, _LineupsResponse, _EventStatisticsResponse, 
    _CountryChannelsResponse, _RankingsResponse, _SeasonRoundsResponse,
    _SearchResultData, _RacingStandingsEntryData,
    _ChannelData, _ChannelScheduleResponse
)


logger = logging.getLogger(__name__)

@contextmanager
def ignore_not_found(context_info=""):
    """Catches ProviderNotFoundError, logs it as a warning, and lets the code continue."""
    try:
        yield
    except ProviderNotFoundError as e:
        logger.warning(f"Ignored expected 404: {context_info} | Details: {e}")

@pytest.fixture(scope="module")
def provider():
    fetcher = RecordingFetcher(mode="auto", cache_dir="tests/mock_data")
    return SofascoreProvider(fetcher=fetcher, fetch_delay=0.1)

# =====================================================================
# 1. Categories
# =====================================================================

def test_get_categories(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        sport = data.get("sport")
        if sport:
            result = provider.get_categories(sport)
            assert isinstance(result, list)
            if result:
                assert isinstance(result[0], _CategoryData)

def test_get_category_unique_tournaments(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for tourney in data.get("tournaments", []):
            if "category_id" in tourney:
                result = provider.get_category_unique_tournaments(tourney["category_id"])
                assert isinstance(result, list)
                if result:
                    assert isinstance(result[0], _UniqueTournamentData)

def test_get_category_unique_stages(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for stage in data.get("stages", []):
            if "category_id" in stage:
                result = provider.get_category_unique_stages(stage["category_id"])
                assert isinstance(result, list)
                if result:
                    assert isinstance(result[0], _UniqueStageData)

# =====================================================================
# 2. Tournaments & Seasons
# =====================================================================

def test_get_unique_tournament(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for tourney in data.get("tournaments", []):
            if "unique_tournament_id" in tourney:
                result = provider.get_unique_tournament(tourney["unique_tournament_id"])
                assert isinstance(result, _UniqueTournamentData)

def test_get_unique_tournament_seasons(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for tourney in data.get("tournaments", []):
            if "unique_tournament_id" in tourney:
                result = provider.get_unique_tournament_seasons(tourney["unique_tournament_id"])
                assert isinstance(result, list)
                if result:
                    assert isinstance(result[0], _SeasonData)

def test_get_unique_tournament_rounds(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for tourney in data.get("tournaments", []):
            if "unique_tournament_id" in tourney and "season_id" in tourney:
                with ignore_not_found(f"Domain: {domain}, Tournament ID: {tourney['unique_tournament_id']}, Season ID: {tourney['season_id']}"):
                    result = provider.get_unique_tournament_rounds(
                        tourney["unique_tournament_id"], tourney["season_id"]
                    )
                    assert isinstance(result, _SeasonRoundsResponse)

def test_get_unique_tournament_standings(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain not in ["football", "basketball"]: continue
        for tourney in data.get("tournaments", []):
            if "unique_tournament_id" in tourney and "season_id" in tourney:
                result = provider.get_unique_tournament_standings(
                    tourney["unique_tournament_id"], tourney["season_id"]
                )
                assert isinstance(result, list)
                if result:
                    assert isinstance(result[0], _TeamStandingsData)

def test_get_unique_tournament_fixtures(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for tourney in data.get("tournaments", []):
            if "unique_tournament_id" in tourney and "season_id" in tourney:
                with ignore_not_found(f"Domain: {domain}, Tournament ID: {tourney['unique_tournament_id']}, Season ID: {tourney['season_id']}"):
                    result = provider.get_unique_tournament_fixtures(
                        tourney["unique_tournament_id"], tourney["season_id"]
                    )
                    assert isinstance(result, _EventsResponse)

def test_get_unique_tournament_results(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for tourney in data.get("tournaments", []):
            if "unique_tournament_id" in tourney and "season_id" in tourney:
                with ignore_not_found(f"Domain: {domain}, Tournament ID: {tourney['unique_tournament_id']}, Season ID: {tourney['season_id']}"):
                    result = provider.get_unique_tournament_results(
                        tourney["unique_tournament_id"], tourney["season_id"]
                    )
                    assert isinstance(result, _EventsResponse)

# =====================================================================
# 3. Teams
# =====================================================================

def test_get_team(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for team_id in data.get("teams", []):
            result = provider.get_team(team_id)
            assert isinstance(result, _TeamResponse)

def test_get_team_seasons(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for team_id in data.get("teams", []):
            with ignore_not_found(f"Domain: {domain}, Team ID: {team_id}"):
                result = provider.get_team_seasons(team_id)
                assert isinstance(result, list)
                if result:
                    assert isinstance(result[0], _UniqueTournamentSeasonsResponse)

def test_get_team_fixtures_and_results(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for team_id in data.get("teams", []):
            with ignore_not_found(f"Domain: {domain}, Team ID: {team_id}"):
                fixtures = provider.get_team_fixtures(team_id)
                assert isinstance(fixtures, _EventsResponse)
            with ignore_not_found(f"Domain: {domain}, Team ID: {team_id}"):
                results = provider.get_team_results(team_id)
                assert isinstance(results, _EventsResponse)

def test_get_team_players(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for team_id in data.get("teams", []):
            with ignore_not_found(f"Domain: {domain}, Team ID: {team_id}"):
                result = provider.get_team_players(team_id)
                assert isinstance(result, TeamPlayers)

def test_get_team_year_statistics(provider: SofascoreProvider):
    # Tennis specific test
    tennis_teams = TEST_CONFIG.get("tennis", {}).get("teams", [])
    if tennis_teams:
        for team_id in tennis_teams:
            result = provider.get_team_year_statistics(team_id, "2024")
            assert isinstance(result, list)
            if result:
                assert isinstance(result[0], TeamYearSurfaceStats)

# def test_get_team_season_stats(provider: SofascoreProvider):
#     # Relies on linking a team to a tournament. We'll use football.
#     teams = TEST_CONFIG.get("football", {}).get("teams", [])
#     tournaments = TEST_CONFIG.get("football", {}).get("tournaments", [])
#     if teams and tournaments:
#         for team_id in teams:
#             with ignore_not_found(f"Domain: football, Team ID: {team_id}, Tournament ID: {tournaments[0]['unique_tournament_id']}, Season ID: {tournaments[0]['season_id']}"):
#                 result = provider.get_team_season_stats(
#                     team_id,
#                     tournaments["unique_tournament_id"],
#                     tournaments["season_id"]
#                 )
#                 assert isinstance(result, TeamSeasonStats)

# =====================================================================
# 4. Players, Managers, Referees, Venues
# =====================================================================

def test_get_player(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for player_id in data.get("players", []):
            result = provider.get_player(player_id)
            assert isinstance(result, _PlayerData)

def test_get_player_statistics(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for player_id in data.get("players", []):
            with ignore_not_found(f"Domain: {domain}, Player ID: {player_id}"):
                result = provider.get_player_statistics(player_id)
                assert isinstance(result, list)
                if result:
                    assert isinstance(result[0], PlayerSeasonStats)

def test_get_manager(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for manager_id in data.get("managers", []):
            result = provider.get_manager(manager_id)
            assert isinstance(result, _ManagerData)

def test_get_manager_career_history(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for manager_id in data.get("managers", []):
            result = provider.get_manager_career_history(manager_id)
            assert isinstance(result, list)
            if result:
                assert isinstance(result[0], ManagerTenure)

def test_get_referee_and_venue(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for referee_id in data.get("referees", []):
            result = provider.get_referee(referee_id)
            assert isinstance(result, _RefereeData)
        for venue_id in data.get("venues", []):
            result = provider.get_venue(venue_id)
            assert isinstance(result, _VenueData)

# =====================================================================
# 5. Events & Match Details
# =====================================================================

def test_get_event(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for event in data.get("events", []):
            result = provider.get_event(event["event_id"])
            assert isinstance(result, _EventData)

def test_get_event_details(provider: SofascoreProvider):
    # Test all event-related endpoints using the first available event ID
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for event in data.get("events", []):
            event_id = event["event_id"]

            with ignore_not_found(f"Domain: {domain}, Event ID: {event_id}"):
                lineups = provider.get_event_lineups(event_id)
                assert isinstance(lineups, _LineupsResponse)

            with ignore_not_found(f"Domain: {domain}, Event ID: {event_id}"):
                incidents = provider.get_event_incidents(event_id)
                assert isinstance(incidents, list)

            with ignore_not_found(f"Domain: {domain}, Event ID: {event_id}"):
                stats = provider.get_event_statistics(event_id)
                assert isinstance(stats, _EventStatisticsResponse)

            with ignore_not_found(f"Domain: {domain}, Event ID: {event_id}"):
                channels = provider.get_event_channels(event_id)
                assert isinstance(channels, _CountryChannelsResponse)

def test_get_h2h_history(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        for event in data.get("events", []):
            if "event_custom_id" in event and event["event_custom_id"]:
                with ignore_not_found(f"Domain: {domain}, Event Custom ID: {event['event_custom_id']}"):
                    result = provider.get_h2h_history(event["event_custom_id"])
                    assert isinstance(result, _EventsResponse)

def test_get_scheduled_events(provider: SofascoreProvider):
    for domain, data in TEST_CONFIG.items():
        if domain in ["misc", "errors"]: continue
        sport = data.get("sport")
        for date in data.get("valid_dates", []):
            result = provider.get_scheduled_events(sport, date)
            assert isinstance(result, _EventsResponse)

# =====================================================================
# 6. Motorsport / Cycling Stages
# =====================================================================

def test_get_stage_endpoints(provider: SofascoreProvider):
    for domain in ["motorsport", "cycling"]:
        data = TEST_CONFIG.get(domain, {})
        for stage in data.get("stages", []):
            if "stage_id" not in stage: continue
            
            stage_id = stage["stage_id"]
            
            res_stage = provider.get_stage(stage_id)
            assert isinstance(res_stage, _StageData)

            with ignore_not_found(f"Domain: {domain}, Stage ID: {stage_id}"):
                res_standings_c = provider.get_stage_standings_competitors(stage_id)
                assert isinstance(res_standings_c, list)
                if res_standings_c:
                    assert isinstance(res_standings_c[0], _RacingStandingsEntryData)

            with ignore_not_found(f"Domain: {domain}, Stage ID: {stage_id}"):
                res_standings_t = provider.get_stage_standings_teams(stage_id)
                assert isinstance(res_standings_t, list)
                if res_standings_t:
                    assert isinstance(res_standings_t[0], _RacingStandingsEntryData)

def test_motorsport_team_specifics(provider: SofascoreProvider):
    teams = TEST_CONFIG.get("motorsport", {}).get("teams", [])
    stages = TEST_CONFIG.get("motorsport", {}).get("stages", [])
    
    if teams and stages:
        for team_id in teams:
            seasons = provider.get_team_stage_seasons(team_id)
            assert isinstance(seasons, list)
            if seasons:
                assert isinstance(seasons[0], _StageData)
                
            history = provider.get_team_driver_career_history(team_id)
            assert isinstance(history, list)
            if history:
                assert isinstance(history[0], DriverCareerHistory)

            for stage in stages:
                races = provider.get_team_stage_races(team_id, stage["stage_season_id"])
                assert isinstance(races, list)
                if races:
                    assert isinstance(races[0], RaceResults)

# =====================================================================
# 7. TV Channels & Rankings (Misc)
# =====================================================================

def test_get_rankings(provider: SofascoreProvider):
    for ranking_id in TEST_CONFIG["misc"].get("rankings", []):
        result = provider.get_ranking(ranking_id)
        assert isinstance(result, _RankingsResponse)

def test_get_country_channels(provider: SofascoreProvider):
    for code in TEST_CONFIG["misc"].get("country_codes", []):
        result = provider.get_country_channels(code)
        assert isinstance(result, list)
        if result:
            assert isinstance(result[0], _ChannelData)

def test_get_channel_schedule(provider: SofascoreProvider):
    for channel_id in TEST_CONFIG["misc"].get("channels", []):
        result = provider.get_channel_schedule(channel_id)
        assert isinstance(result, _ChannelScheduleResponse)

# =====================================================================
# 8. Search
# =====================================================================

def test_search_endpoints(provider: SofascoreProvider):
    queries = ["Paris", "Real"]
    for query in queries:
        res_all = provider.search_all(query)
        assert isinstance(res_all, list)
        if res_all:
            assert isinstance(res_all[0], _SearchResultData)

        res_teams = provider.search_teams(query)
        assert isinstance(res_teams, list)
        if res_teams:
            assert isinstance(res_teams[0], _SearchResultData)
            assert isinstance(res_teams[0].entity, _TeamData)

        res_players = provider.search_players(query)
        assert isinstance(res_players, list)
        if res_players:
            assert isinstance(res_players[0], _SearchResultData)
            assert isinstance(res_players[0].entity, _PlayerData)

        res_persons = provider.search_player_team_persons(query)
        assert isinstance(res_persons, list)
        if res_persons:
            assert isinstance(res_persons[0], _SearchResultData)
            assert isinstance(res_persons[0].entity, (_PlayerData, _TeamData))

# =====================================================================
# 9. Boundaries / Errors
# =====================================================================

def test_invalid_date_format(provider: SofascoreProvider):
    with pytest.raises(TypeError, match="Invalid date format"):
        provider.get_scheduled_events("football", TEST_CONFIG["errors"]["invalid_date"])
