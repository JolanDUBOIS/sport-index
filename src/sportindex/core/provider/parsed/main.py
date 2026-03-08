from __future__ import annotations

from .models import (
    ParsedCategory,
    ParsedChannel,
    ParsedChannelScheduleResponse,
    ParsedCountryChannelsResponse,
    ParsedDriverCareerHistory,
    ParsedDriverPerformance,
    ParsedEvent,
    ParsedEventsResponse,
    ParsedEventStatisticsResponse,
    ParsedIncident,
    ParsedLineupsResponse,
    ParsedManager,
    ParsedManagerCareerHistoryItem,
    ParsedMomentumGraphResponse,
    ParsedPlayer,
    ParsedPlayerSeasonStats,
    ParsedRaceResults,
    ParsedRacingStandingsEntry,
    ParsedRankingsResponse,
    ParsedReferee,
    ParsedSearchResult,
    ParsedSeason,
    ParsedStage,
    ParsedTeamSeasonStats,
    ParsedTeamPlayers,
    ParsedTeamResponse,
    ParsedTeamStandings,
    ParsedTeamYearStats,
    ParsedTournament,
    ParsedUniqueStage,
    ParsedUniqueTournament,
    ParsedUniqueTournamentSeasonsResponse,
    ParsedVenue,
)
from ..raw import SofascoreProvider


class ParsedSofascoreProvider:
    """Parsed wrapper around `SofascoreProvider`."""

    def __init__(self, fetch_delay: float = 0.5):
        self._provider = SofascoreProvider(fetch_delay=fetch_delay)

    # ---- Categories ---- #

    def get_categories(self, sport: str) -> list[ParsedCategory]:
        raw = self._provider.get_categories(sport=sport)
        return [ParsedCategory.from_raw(item) for item in raw]

    def get_category_unique_tournaments(self, category_id: str) -> list[ParsedUniqueTournament]:
        raw = self._provider.get_category_unique_tournaments(category_id=category_id)
        return [ParsedUniqueTournament.from_raw(item) for item in raw]

    def get_category_unique_stages(self, category_id: str) -> list[ParsedUniqueStage]:
        raw = self._provider.get_category_unique_stages(category_id=category_id)
        return [ParsedUniqueStage.from_raw(item) for item in raw]

    # ---- Unique Tournaments ---- #

    def get_unique_tournament(self, unique_tournament_id: str) -> ParsedUniqueTournament:
        raw = self._provider.get_unique_tournament(unique_tournament_id=unique_tournament_id)
        return ParsedUniqueTournament.from_raw(raw)

    def get_unique_tournament_seasons(self, unique_tournament_id: str) -> list[ParsedSeason]:
        raw = self._provider.get_unique_tournament_seasons(unique_tournament_id=unique_tournament_id)
        return [ParsedSeason.from_raw(item) for item in raw]

    def get_unique_tournament_standings(
        self,
        unique_tournament_id: str,
        season_id: str,
        view: str = "total",
    ) -> list[ParsedTeamStandings]:
        raw = self._provider.get_unique_tournament_standings(
            unique_tournament_id=unique_tournament_id,
            season_id=season_id,
            view=view,
        )
        return [ParsedTeamStandings.from_raw(item) for item in raw]

    def get_unique_tournament_fixtures(
        self,
        unique_tournament_id: str,
        season_id: str,
        page: int = 0,
    ) -> ParsedEventsResponse:
        raw = self._provider.get_unique_tournament_fixtures(
            unique_tournament_id=unique_tournament_id,
            season_id=season_id,
            page=page,
        )
        return ParsedEventsResponse.from_raw(raw)

    def get_unique_tournament_results(
        self,
        unique_tournament_id: str,
        season_id: str,
        page: int = 0,
    ) -> ParsedEventsResponse:
        raw = self._provider.get_unique_tournament_results(
            unique_tournament_id=unique_tournament_id,
            season_id=season_id,
            page=page,
        )
        return ParsedEventsResponse.from_raw(raw)

    # ---- Tournaments ---- #

    def get_tournament(self, tournament_id: str) -> ParsedTournament:
        raw = self._provider.get_tournament(tournament_id=tournament_id)
        return ParsedTournament.from_raw(raw)

    # ---- Teams ---- #

    def get_team(self, team_id: str) -> ParsedTeamResponse:
        raw = self._provider.get_team(team_id=team_id)
        return ParsedTeamResponse.from_raw(raw)

    def get_team_seasons(self, team_id: str) -> list[ParsedUniqueTournamentSeasonsResponse]:
        raw = self._provider.get_team_seasons(team_id=team_id)
        return [ParsedUniqueTournamentSeasonsResponse.from_raw(item) for item in raw]

    def get_team_fixtures(self, team_id: str, page: int = 0) -> ParsedEventsResponse:
        raw = self._provider.get_team_fixtures(team_id=team_id, page=page)
        return ParsedEventsResponse.from_raw(raw)

    def get_team_results(self, team_id: str, page: int = 0) -> ParsedEventsResponse:
        raw = self._provider.get_team_results(team_id=team_id, page=page)
        return ParsedEventsResponse.from_raw(raw)

    def get_team_players(self, team_id: str) -> ParsedTeamPlayers:
        raw = self._provider.get_team_players(team_id=team_id)
        return ParsedTeamPlayers.from_raw(raw)

    def get_team_year_statistics(self, team_id: str, year: str) -> ParsedTeamYearStats:
        raw = self._provider.get_team_year_statistics(team_id=team_id, year=year)
        return ParsedTeamYearStats.from_raw(raw)

    def get_team_season_stats(
        self,
        team_id: str,
        unique_tournament_id: str,
        season_id: str,
    ) -> ParsedTeamSeasonStats:
        raw = self._provider.get_team_season_stats(
            team_id=team_id,
            unique_tournament_id=unique_tournament_id,
            season_id=season_id,
        )
        return ParsedTeamSeasonStats.from_raw(raw)

    def get_team_stage_seasons(self, team_id: str) -> list[ParsedStage]:
        raw = self._provider.get_team_stage_seasons(team_id=team_id)
        return [ParsedStage.from_raw(item) for item in raw]

    def get_team_stage_races(self, team_id: str, stage_season_id: str) -> list[ParsedRaceResults]:
        raw = self._provider.get_team_stage_races(team_id=team_id, stage_season_id=stage_season_id)
        return [ParsedRaceResults.from_raw(item) for item in raw]

    def get_team_driver_career_history(self, team_id: str) -> list[ParsedDriverCareerHistory]:
        raw = self._provider.get_team_driver_career_history(team_id=team_id)
        return [ParsedDriverCareerHistory.from_raw(item) for item in raw]

    # ---- Players ---- #

    def get_player(self, player_id: str) -> ParsedPlayer:
        raw = self._provider.get_player(player_id=player_id)
        return ParsedPlayer.from_raw(raw)

    def get_player_results(self, player_id: str, page: int = 0) -> ParsedEventsResponse:
        raw = self._provider.get_player_results(player_id=player_id, page=page)
        return ParsedEventsResponse.from_raw(raw)

    def get_player_statistics(self, player_id: str) -> list[ParsedPlayerSeasonStats]:
        raw = self._provider.get_player_statistics(player_id=player_id)
        return [ParsedPlayerSeasonStats.from_raw(item) for item in raw]

    def get_player_seasons(self, player_id: str) -> list[ParsedUniqueTournamentSeasonsResponse]:
        raw = self._provider.get_player_seasons(player_id=player_id)
        return [ParsedUniqueTournamentSeasonsResponse.from_raw(item) for item in raw]

    # ---- Managers ---- #

    def get_manager(self, manager_id: str) -> ParsedManager:
        raw = self._provider.get_manager(manager_id=manager_id)
        return ParsedManager.from_raw(raw)

    def get_manager_results(self, manager_id: str, page: int = 0) -> ParsedEventsResponse:
        raw = self._provider.get_manager_results(manager_id=manager_id, page=page)
        return ParsedEventsResponse.from_raw(raw)

    def get_manager_career_history(self, manager_id: str) -> list[ParsedManagerCareerHistoryItem]:
        raw = self._provider.get_manager_career_history(manager_id=manager_id)
        return [ParsedManagerCareerHistoryItem.from_raw(item) for item in raw]

    # ---- Referees ---- #

    def get_referee(self, referee_id: str) -> ParsedReferee:
        raw = self._provider.get_referee(referee_id=referee_id)
        return ParsedReferee.from_raw(raw)

    def get_referee_results(self, referee_id: str, page: int = 0) -> ParsedEventsResponse:
        raw = self._provider.get_referee_results(referee_id=referee_id, page=page)
        return ParsedEventsResponse.from_raw(raw)

    # ---- Venues ---- #

    def get_venue(self, venue_id: str) -> ParsedVenue:
        raw = self._provider.get_venue(venue_id=venue_id)
        return ParsedVenue.from_raw(raw)

    def get_venue_fixtures(self, venue_id: str, page: int = 1) -> ParsedEventsResponse:
        raw = self._provider.get_venue_fixtures(venue_id=venue_id, page=page)
        return ParsedEventsResponse.from_raw(raw)

    def get_venue_results(self, venue_id: str, page: int = 1) -> ParsedEventsResponse:
        raw = self._provider.get_venue_results(venue_id=venue_id, page=page)
        return ParsedEventsResponse.from_raw(raw)

    # ---- Events ---- #

    def get_event(self, event_id: str) -> ParsedEvent:
        raw = self._provider.get_event(event_id=event_id)
        return ParsedEvent.from_raw(raw)

    def get_lineups(self, event_id: str) -> ParsedLineupsResponse:
        raw = self._provider.get_lineups(event_id=event_id)
        return ParsedLineupsResponse.from_raw(raw)

    def get_incidents(self, event_id: str) -> list[ParsedIncident]:
        raw = self._provider.get_incidents(event_id=event_id)
        return [ParsedIncident.from_raw(item) for item in raw]

    def get_event_statistics(self, event_id: str) -> ParsedEventStatisticsResponse:
        raw = self._provider.get_event_statistics(event_id=event_id)
        return ParsedEventStatisticsResponse.from_raw(raw)

    def get_event_graph(self, event_id: str) -> ParsedMomentumGraphResponse:
        raw = self._provider.get_event_graph(event_id=event_id)
        return ParsedMomentumGraphResponse.from_raw(raw)

    def get_channels(self, event_id: str) -> ParsedCountryChannelsResponse:
        raw = self._provider.get_channels(event_id=event_id)
        return ParsedCountryChannelsResponse.from_raw(raw)

    def get_h2h_history(self, event_custom_id: str) -> ParsedEventsResponse:
        raw = self._provider.get_h2h_history(event_custom_id=event_custom_id)
        return ParsedEventsResponse.from_raw(raw)

    def get_scheduled_events(self, sport: str, date: str) -> ParsedEventsResponse:
        raw = self._provider.get_scheduled_events(sport=sport, date=date)
        return ParsedEventsResponse.from_raw(raw)

    # ---- Rankings ---- #

    def get_ranking(self, ranking_id: str) -> ParsedRankingsResponse:
        raw = self._provider.get_ranking(ranking_id=ranking_id)
        return ParsedRankingsResponse.from_raw(raw)

    # ---- Motorsport ---- #

    def get_unique_stage_seasons(self, unique_stage_id: str) -> list[ParsedStage]:
        raw = self._provider.get_unique_stage_seasons(unique_stage_id=unique_stage_id)
        return [ParsedStage.from_raw(item) for item in raw]

    def get_stage(self, stage_id: str) -> ParsedStage:
        raw = self._provider.get_stage(stage_id=stage_id)
        return ParsedStage.from_raw(raw)

    def get_stage_substages(self, stage_id: str) -> list[ParsedStage]:
        raw = self._provider.get_stage_substages(stage_id=stage_id)
        return [ParsedStage.from_raw(item) for item in raw]

    def get_stage_details(self, stage_id: str) -> ParsedStage:
        raw = self._provider.get_stage_details(stage_id=stage_id)
        return ParsedStage.from_raw(raw)

    def get_stage_standings_competitors(self, stage_id: str) -> list[ParsedRacingStandingsEntry]:
        raw = self._provider.get_stage_standings_competitors(stage_id=stage_id)
        return [ParsedRacingStandingsEntry.from_raw(item) for item in raw]

    def get_stage_standings_teams(self, stage_id: str) -> list[ParsedRacingStandingsEntry]:
        raw = self._provider.get_stage_standings_teams(stage_id=stage_id)
        return [ParsedRacingStandingsEntry.from_raw(item) for item in raw]

    def get_stage_drivers_performance(self, team_id: str, stage_id: str) -> list[ParsedDriverPerformance]:
        raw = self._provider.get_stage_drivers_performance(team_id=team_id, stage_id=stage_id)
        return [ParsedDriverPerformance.from_raw(item) for item in raw]

    # ---- TV Channels ---- #

    def get_country_channels(self, country_code: str) -> list[ParsedChannel]:
        raw = self._provider.get_country_channels(country_code=country_code)
        return [ParsedChannel.from_raw(item) for item in raw]

    def get_channel_schedule(self, channel_id: str) -> ParsedChannelScheduleResponse:
        raw = self._provider.get_channel_schedule(channel_id=channel_id)
        return ParsedChannelScheduleResponse.from_raw(raw)

    # ---- Search ---- #

    def search_all(self, query: str, page: int = 0) -> list[ParsedSearchResult]:
        raw = self._provider.search_all(query=query, page=page)
        return [ParsedSearchResult.from_raw(item) for item in raw]

    def search_unique_tournaments(self, query: str, page: int = 0) -> list[ParsedSearchResult]:
        raw = self._provider.search_unique_tournaments(query=query, page=page)
        return [ParsedSearchResult.from_raw(item) for item in raw]

    def search_teams(self, query: str, page: int = 0) -> list[ParsedSearchResult]:
        raw = self._provider.search_teams(query=query, page=page)
        return [ParsedSearchResult.from_raw(item) for item in raw]

    def search_events(self, query: str, page: int = 0) -> list[ParsedSearchResult]:
        raw = self._provider.search_events(query=query, page=page)
        return [ParsedSearchResult.from_raw(item) for item in raw]

    def search_players(self, query: str, page: int = 0) -> list[ParsedSearchResult]:
        raw = self._provider.search_players(query=query, page=page)
        return [ParsedSearchResult.from_raw(item) for item in raw]

    def search_managers(self, query: str, page: int = 0) -> list[ParsedSearchResult]:
        raw = self._provider.search_managers(query=query, page=page)
        return [ParsedSearchResult.from_raw(item) for item in raw]

    def search_referees(self, query: str, page: int = 0) -> list[ParsedSearchResult]:
        raw = self._provider.search_referees(query=query, page=page)
        return [ParsedSearchResult.from_raw(item) for item in raw]

    def search_venues(self, query: str, page: int = 0) -> list[ParsedSearchResult]:
        raw = self._provider.search_venues(query=query, page=page)
        return [ParsedSearchResult.from_raw(item) for item in raw]
