"""
Sofascore provider — returns raw API dicts annotated with TypedDicts.

This is a drop-in replacement for the original SofascoreProvider that
removes the model layer entirely. Every method returns the raw API
response (or an extracted sub-dict), annotated with TypedDicts so
your IDE knows what keys are available.

For complex transformations (periods, incidents), use the functions
in parsers.py.

Reuses fetcher, endpoints, and exceptions from the existing provider.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from .fetcher import Fetcher
from .endpoints import ENDPOINTS

from .types import (
    RawCategory,
    RawChannel,
    RawChannelScheduleResponse,
    RawDriverCareerHistory,
    RawDriverPerformance,
    RawEvent,
    RawEventsResponse,
    RawEventStatisticsResponse,
    RawIncident,
    RawLineupsResponse,
    RawManager,
    RawManagerCareerHistoryItem,
    RawMomentumGraphResponse,
    RawPlayer,
    RawPlayerSeasonStats,
    RawRaceResults,
    RawRacingStandingsEntry,
    RawRankingsResponse,
    RawReferee,
    RawSearchResult,
    RawTeamResponse,
    RawSeason,
    RawStage,
    RawTeamPlayers,
    RawTeamSeasonStats,
    RawTeamStandings,
    RawTeamYearStats,
    RawTournament,
    RawUniqueStage,
    RawUniqueTournament,
    RawUniqueTournamentSeasonsResponse,
    RawVenue,
)

logger = logging.getLogger(__name__)


class SofascoreProvider:
    """Raw data provider for Sofascore internal endpoints.

    Every public method returns plain dicts (JSON from the API).
    Return types are annotated with TypedDicts for IDE autocompletion
    and static analysis — but at runtime these are regular dicts.

    REMARK: The `raw` parameter from the old provider is gone.
    Everything IS raw now. The higher layer (core/models) handles
    coercion into domain objects.
    """

    def __init__(self, fetch_delay: float = 0.5):
        self.fetcher = Fetcher()
        self.fetch_delay = fetch_delay

    # ---- Categories ---- #

    def get_categories(self, sport: str) -> list[RawCategory]:
        """Fetch all categories for the sport."""
        url = self._format("all-categories", sport=sport)
        data = self._fetch(url)
        return data.get("categories", [])

    def get_category_unique_tournaments(self, category_id: str) -> list[RawUniqueTournament]:
        """Fetch unique tournaments for a specific category.

        REMARK: The API nests UTs inside `groups[].uniqueTournaments[]`.
        This method flattens them into a single list.
        """
        url = self._format("category-unique-tournaments", category_id=category_id)
        data = self._fetch(url)
        return [
            ut
            for group in data.get("groups", [])
            for ut in group.get("uniqueTournaments", [])
        ]

    def get_category_unique_stages(self, category_id: str) -> list[RawUniqueStage]:
        """Fetch unique stages for a specific category."""
        url = self._format("category-unique-stages", category_id=category_id)
        data = self._fetch(url)
        return data.get("uniqueStages", [])

    # ---- Unique Tournaments ---- #

    def get_unique_tournament(self, unique_tournament_id: str) -> RawUniqueTournament:
        """Fetch unique tournament details."""
        url = self._format("unique-tournament", unique_tournament_id=unique_tournament_id)
        data = self._fetch(url)
        return data.get("uniqueTournament", {})

    def get_unique_tournament_seasons(self, unique_tournament_id: str) -> list[RawSeason]:
        """Fetch seasons for a unique tournament."""
        url = self._format("unique-tournament-seasons", unique_tournament_id=unique_tournament_id)
        data = self._fetch(url)
        return data.get("seasons", [])

    def get_unique_tournament_standings(
        self,
        unique_tournament_id: str,
        season_id: str,
        view: str = "total",
    ) -> list[RawTeamStandings]:
        """Fetch standings for a unique tournament + season."""
        url = self._format(
            "unique-tournament-standings",
            unique_tournament_id=unique_tournament_id,
            season_id=season_id,
            view=view,
        )
        data = self._fetch(url)
        return data.get("standings", [])

    def get_unique_tournament_fixtures(
        self,
        unique_tournament_id: str,
        season_id: str,
        page: int = 0,
    ) -> RawEventsResponse:
        """Fetch upcoming fixtures for a unique tournament + season."""
        url = self._format(
            "unique-tournament-fixtures",
            unique_tournament_id=unique_tournament_id,
            season_id=season_id,
            page=page,
        )
        return self._fetch(url)

    def get_unique_tournament_results(
        self,
        unique_tournament_id: str,
        season_id: str,
        page: int = 0,
    ) -> RawEventsResponse:
        """Fetch recent results for a unique tournament + season."""
        url = self._format(
            "unique-tournament-results",
            unique_tournament_id=unique_tournament_id,
            season_id=season_id,
            page=page,
        )
        return self._fetch(url)

    # ---- Tournaments ---- #

    def get_tournament(self, tournament_id: str) -> RawTournament:
        """Fetch tournament details."""
        url = self._format("tournament", tournament_id=tournament_id)
        data = self._fetch(url)
        return data.get("tournament", {})

    # ---- Teams ---- #

    def get_team(self, team_id: str) -> RawTeamResponse:
        """Fetch team details."""
        url = self._format("team", team_id=team_id)
        return self._fetch(url)

    def get_team_seasons(self, team_id: str) -> list[RawUniqueTournamentSeasonsResponse]:
        """Fetch seasons for a team (grouped by unique tournament)."""
        url = self._format("team-seasons", team_id=team_id)
        data = self._fetch(url)
        return data.get("uniqueTournamentSeasons", [])

    def get_team_fixtures(self, team_id: str, page: int = 0) -> RawEventsResponse:
        """Fetch upcoming fixtures for a team."""
        url = self._format("team-fixtures", team_id=team_id, page=page)
        return self._fetch(url)

    def get_team_results(self, team_id: str, page: int = 0) -> RawEventsResponse:
        """Fetch recent results for a team."""
        url = self._format("team-results", team_id=team_id, page=page)
        return self._fetch(url)

    def get_team_players(self, team_id: str) -> RawTeamPlayers:
        """Fetch players for a team."""
        url = self._format("team-players", team_id=team_id)
        return self._fetch(url)

    def get_team_year_statistics(self, team_id: str, year: str) -> RawTeamYearStats:
        """Fetch year statistics for a team (tennis only)."""
        url = self._format("team-year-statistics", team_id=team_id, year=year)
        data = self._fetch(url)
        return data.get("statistics", {})

    def get_team_season_stats(
        self,
        team_id: str,
        unique_tournament_id: str,
        season_id: str,
    ) -> RawTeamSeasonStats:
        """Fetch season statistics for a team."""
        url = self._format(
            "team-season-stats",
            team_id=team_id,
            unique_tournament_id=unique_tournament_id,
            season_id=season_id,
        )
        data = self._fetch(url)
        return data.get("statistics", {})

    def get_team_stage_seasons(self, team_id: str) -> list[RawStage]:
        """Fetch stage seasons for a team (motorsport)."""
        url = self._format("team-stage-seasons", team_id=team_id)
        data = self._fetch(url)
        return data.get("stageSeasons", [])

    def get_team_stage_races(self, team_id: str, stage_season_id: str) -> list[RawRaceResults]:
        """Fetch races for a team + season stage (motorsport)."""
        url = self._format("team-stage-season-races", team_id=team_id, stage_season_id=stage_season_id)
        data = self._fetch(url)
        return data.get("races", [])

    def get_team_driver_career_history(self, team_id: str) -> list[RawDriverCareerHistory]:
        """Fetch driver career history for a team (motorsport)."""
        url = self._format("team-driver-career-history", team_id=team_id)
        return self._fetch(url)

    # ---- Players ---- #

    def get_player(self, player_id: str) -> RawPlayer:
        """Fetch player details."""
        url = self._format("player", player_id=player_id)
        data = self._fetch(url)
        return data.get("player", {})

    def get_player_results(self, player_id: str, page: int = 0) -> RawEventsResponse:
        """Fetch recent results for a player."""
        url = self._format("player-results", player_id=player_id, page=page)
        return self._fetch(url)

    def get_player_statistics(self, player_id: str) -> list[RawPlayerSeasonStats]:
        """Fetch statistics for a player (grouped by season)."""
        url = self._format("player-statistics", player_id=player_id)
        data = self._fetch(url)
        return data.get("seasons", [])

    def get_player_seasons(self, player_id: str) -> list[RawUniqueTournamentSeasonsResponse]:
        """Fetch seasons for a player (grouped by unique tournament)."""
        url = self._format("player-seasons", player_id=player_id)
        data = self._fetch(url)
        return data.get("uniqueTournamentSeasons", [])

    # ---- Managers ---- #

    def get_manager(self, manager_id: str) -> RawManager:
        """Fetch manager details."""
        url = self._format("manager", manager_id=manager_id)
        data = self._fetch(url)
        return data.get("manager", {})

    def get_manager_results(self, manager_id: str, page: int = 0) -> RawEventsResponse:
        """Fetch recent results for a manager."""
        url = self._format("manager-results", manager_id=manager_id, page=page)
        return self._fetch(url)

    def get_manager_career_history(self, manager_id: str) -> list[RawManagerCareerHistoryItem]:
        """Fetch career history for a manager."""
        url = self._format("manager-career-history", manager_id=manager_id)
        data = self._fetch(url)
        return data.get("careerHistory", []) if data else []

    # ---- Referees ---- #

    def get_referee(self, referee_id: str) -> RawReferee:
        """Fetch referee details."""
        url = self._format("referee", referee_id=referee_id)
        data = self._fetch(url)
        return data.get("referee", {})

    def get_referee_results(self, referee_id: str, page: int = 0) -> RawEventsResponse:
        """Fetch recent results for a referee."""
        url = self._format("referee-results", referee_id=referee_id, page=page)
        return self._fetch(url)

    # ---- Venues ---- #

    def get_venue(self, venue_id: str) -> RawVenue:
        """Fetch venue details."""
        url = self._format("venue", venue_id=venue_id)
        data = self._fetch(url)
        return data.get("venue", {})

    def get_venue_fixtures(self, venue_id: str, page: int = 1) -> RawEventsResponse:
        """Fetch upcoming fixtures for a venue."""
        url = self._format("venue-fixtures", venue_id=venue_id, page=page)
        return self._fetch(url)

    def get_venue_results(self, venue_id: str, page: int = 1) -> RawEventsResponse:
        """Fetch recent results for a venue."""
        url = self._format("venue-results", venue_id=venue_id, page=page)
        return self._fetch(url)

    # ---- Events ---- #

    def get_event(self, event_id: str) -> RawEvent:
        """Fetch event details.

        REMARK: To extract derived data from this event, use:
          - parsers.parse_periods(event)    → period structure
          - parsers.get_event_outcome(event) → "home"/"away"/"draw"
          - parsers.get_display_score(event) → {"home": int, "away": int}
        """
        url = self._format("event", event_id=event_id)
        data = self._fetch(url)
        return data.get("event", {})

    def get_lineups(self, event_id: str) -> RawLineupsResponse:
        """Fetch lineups for an event."""
        url = self._format("event-lineups", event_id=event_id)
        data = self._fetch(url)
        return data.get("lineups", {})

    def get_incidents(self, event_id: str) -> list[RawIncident]:
        """Fetch raw incidents for an event.

        REMARK: Use parsers.parse_incidents() to enrich with _side/_score
        fields and filter unknown types. Or consume directly — the
        RawIncident TypedDict documents all possible keys.
        """
        url = self._format("event-incidents", event_id=event_id)
        data = self._fetch(url)
        return data.get("incidents", [])

    def get_event_statistics(self, event_id: str) -> RawEventStatisticsResponse:
        """Fetch statistics for an event."""
        url = self._format("event-statistics", event_id=event_id)
        return self._fetch(url)

    def get_event_graph(self, event_id: str) -> RawMomentumGraphResponse:
        """Fetch momentum graph for an event."""
        url = self._format("event-graph", event_id=event_id)
        return self._fetch(url)

    def get_channels(self, event_id: str) -> dict[str, list[str]]:
        """Fetch country → channel mappings for an event.

        REMARK: Returns the `channels` dict directly (country_code → list of channel IDs).
        """
        url = self._format("event-channels", event_id=event_id)
        data = self._fetch(url)
        return data.get("channels", {})

    def get_h2h_history(self, event_custom_id: str) -> RawEventsResponse:
        """Fetch head-to-head history for an event."""
        url = self._format("event-h2h-history", event_custom_id=event_custom_id)
        return self._fetch(url)

    def get_scheduled_events(self, sport: str, date: str) -> RawEventsResponse:
        """Fetch scheduled events for a sport on a specific date (YYYY-MM-DD)."""
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {date}. Expected YYYY-MM-DD.")
        url = self._format("scheduled-events", sport=sport, date=date)
        return self._fetch(url)

    # ---- Rankings ---- #

    def get_ranking(self, ranking_id: str) -> RawRankingsResponse:
        """Fetch a ranking by ID.

        REMARK: The ranking metadata is under data["rankingType"], the rows
        under data["rankingRows"]. This returns the full response dict.
        """
        url = self._format("ranking", ranking_id=ranking_id)
        return self._fetch(url)

    # ---- Motorsport ---- #

    def get_unique_stage_seasons(self, unique_stage_id: str) -> list[RawStage]:
        """Fetch seasons for a stage."""
        url = self._format("unique-stage-seasons", unique_stage_id=unique_stage_id)
        data = self._fetch(url)
        return data.get("seasons", [])

    def get_stage(self, stage_id: str) -> RawStage:
        """Fetch stage details.

        REMARK: get_stage_details() returns more info — consider using that instead.
        """
        url = self._format("stage", stage_id=stage_id)
        data = self._fetch(url)
        return data.get("stage", {})

    def get_stage_substages(self, stage_id: str) -> list[RawStage]:
        """Fetch substages for a stage."""
        url = self._format("substages", stage_id=stage_id)
        data = self._fetch(url)
        return data.get("stages", [])

    def get_stage_details(self, stage_id: str) -> RawStage:
        """Fetch extended details for a stage, including nested substages."""
        url = self._format("stage-details", stage_id=stage_id)
        data = self._fetch(url)
        return data.get("stage", {})

    def get_stage_standings_competitors(self, stage_id: str) -> list[RawRacingStandingsEntry]:
        """Fetch competitor standings for a stage."""
        url = self._format("standings-competitors", stage_id=stage_id)
        data = self._fetch(url)
        return data.get("standings", [])

    def get_stage_standings_teams(self, stage_id: str) -> list[RawRacingStandingsEntry]:
        """Fetch team/driver standings for a stage."""
        url = self._format("standings-teams", stage_id=stage_id)
        data = self._fetch(url)
        return data.get("standings", [])

    def get_stage_drivers_performance(self, team_id: str, stage_id: str) -> list[RawDriverPerformance]:
        """Fetch drivers performance for a team + stage (season stage in motorsport)."""
        url = self._format("stage-drivers-performance", team_id=team_id, stage_id=stage_id)
        data = self._fetch(url)
        return data.get("driverPerformance", [])

    # ---- TV Channels ---- #

    def get_country_channels(self, country_code: str) -> list[RawChannel]:
        """Fetch TV channels for a country."""
        url = self._format("country-channels", country_code=country_code)
        data = self._fetch(url)
        return data.get("channels", [])

    def get_channel_schedule(self, channel_id: str) -> RawChannelScheduleResponse:
        """Fetch schedule for a TV channel."""
        url = self._format("channel-schedule", channel_id=channel_id)
        return self._fetch(url)

    # ---- Search ---- #

    def search_all(self, query: str, page: int = 0) -> list[RawSearchResult]:
        """Search for all entities by name."""
        return self._search("search-all", query, page)

    def search_unique_tournaments(self, query: str, page: int = 0) -> list[RawSearchResult]:
        """Search for unique tournaments by name."""
        return self._search("search-unique-tournaments", query, page)

    def search_teams(self, query: str, page: int = 0) -> list[RawSearchResult]:
        """Search for teams by name."""
        return self._search("search-teams", query, page)

    def search_events(self, query: str, page: int = 0) -> list[RawSearchResult]:
        """Search for events by name."""
        return self._search("search-events", query, page)

    def search_players(self, query: str, page: int = 0) -> list[RawSearchResult]:
        """Search for players by name."""
        return self._search("search-players", query, page)

    def search_managers(self, query: str, page: int = 0) -> list[RawSearchResult]:
        """Search for managers by name."""
        return self._search("search-managers", query, page)

    def search_referees(self, query: str, page: int = 0) -> list[RawSearchResult]:
        """Search for referees by name."""
        return self._search("search-referees", query, page)

    def search_venues(self, query: str, page: int = 0) -> list[RawSearchResult]:
        """Search for venues by name."""
        return self._search("search-venues", query, page)

    # ---- Internal helpers ---- #

    def _search(self, endpoint_name: str, query: str, page: int = 0) -> list[RawSearchResult]:
        """Generic search helper."""
        url = self._format(endpoint_name)
        params = {"q": query, "page": page}
        data = self._fetch(url, params=params, fetch_delay=0)
        return data.get("results", [])

    def _format(self, endpoint_name: str, **kwargs: Any) -> str:
        """Format an endpoint URL from the endpoint registry."""
        if endpoint_name not in ENDPOINTS:
            raise ValueError(f"Endpoint '{endpoint_name}' is not defined.")
        return ENDPOINTS[endpoint_name].format(**kwargs)

    def _fetch(self, url: str, *, params: dict | None = None, fetch_delay: float | None = None) -> dict:
        """Fetch a URL and return the parsed JSON dict."""
        response = self.fetcher.fetch_url(
            url, params=params, initial_delay=fetch_delay if fetch_delay is not None else self.fetch_delay
        )
        return response.json()
