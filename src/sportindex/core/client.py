import copy
from typing import Literal

from . import logger
from .exceptions import RateLimitError, FetchError
from .constants import SPORTS, RANKING_IDS
from .models import (
    BaseModel,
    Category,
    Event,
    Incident,
    Lineup,
    Manager,
    Player,
    Referee,
    RacingStandings,
    Rankings,
    RoundStage,
    Season,
    SeasonStage,
    Sport,
    Team,
    TeamStandings,
    UniqueTournament,
    Venue,
)
from .sofascore import SofascoreProvider


class Client:
    """ TODO """

    def __init__(self, sport: str, **kwargs):
        self.sport = sport
        self.provider = SofascoreProvider(sport=sport, **kwargs)


    # ==================================================================
    # ======================= Static Data Queries ====================== 
    # ==================================================================

    def get_sports(self) -> list[Sport]:
        """ Returns a list of all sports available in the Sofascore database. This is not fetched from the API but hardcoded based on observed data. """
        return copy.deepcopy(SPORTS)


    def get_available_rankings_ids(self) -> dict[str, str]:
        """ Returns a mapping of available ranking IDs to their slug. This is not fetched from the API but hardcoded based on observed data. """
        return copy.deepcopy(RANKING_IDS)


    # ==================================================================
    # =================== Discovery Oriented Queries ===================
    # ==================================================================


    def get_categories(self) -> list[Category]:
        """ Fetch all categories for the sport. """
        try:
            categories_raw = self.provider.get_categories()
            return [Category.from_api(cat) for cat in categories_raw.get("categories", [])]
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch categories from Sofascore.")
            return []


    def get_unique_tournaments(self, category_id: str) -> list[UniqueTournament]:
        """ Fetch all unique tournaments for a given category. """
        try:
            unique_tournaments_raw = self.provider.get_category_unique_tournaments(category_id=category_id)
            groups = unique_tournaments_raw.get("groups", [])
            if not groups or not isinstance(groups, list) or not isinstance(groups[0], dict):
                return []
            unique_tournaments = [UniqueTournament.from_api(tournament) for tournament in groups[0].get("uniqueTournaments", [])]
            return unique_tournaments
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch unique tournaments from Sofascore.")
            return []

    def get_seasons(
        self,
        *,
        unique_tournament_id: str | None = None,
        team_id: str | None = None,
        unique_stage_id: str | None = None,
    ) -> list[Season]:
        """ Fetch seasons for a given unique tournament or team. """
        try:
            if unique_tournament_id is not None:
                if not unique_tournament_id:
                    raise ValueError("unique_tournament_id is required for fetching unique tournament seasons.")
                seasons_raw = self.provider.get_unique_tournament_seasons(unique_tournament_id=unique_tournament_id)
            elif team_id is not None:
                if not team_id:
                    raise ValueError("team_id is required for fetching team seasons.")
                seasons_raw = self.provider.get_team_seasons(team_id=team_id)
            elif unique_stage_id is not None:
                if not unique_stage_id:
                    raise ValueError("unique_stage_id is required for fetching unique stage seasons.")
                seasons_raw = self.provider.get_unique_stage_seasons(unique_stage_id=unique_stage_id)
            else:
                raise ValueError("Invalid target for fetching seasons. Must be 'unique-tournament' or 'team'.")
            return [Season.from_api(season) for season in seasons_raw.get("seasons", [])]
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch seasons from Sofascore.")
            return []


    # ==================================================================
    # ===================== Entity Oriented Queries ====================
    # ==================================================================

    def get_unique_tournament(self, unique_tournament_id: str) -> UniqueTournament | None:
        """ Fetch information about a specific unique tournament. """
        try:
            unique_tournament_raw = self.provider.get_unique_tournament(unique_tournament_id=unique_tournament_id)
            return UniqueTournament.from_api(unique_tournament_raw)
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch unique tournament from Sofascore.")
            return None


    def get_season_stage(self, season_stage_id: str) -> SeasonStage | None:
        """ Fetch information about a specific season stage (racing season). """
        try:
            stage_raw = self.provider.get_stage_details(season_stage_id=season_stage_id)
            return SeasonStage.from_api(stage_raw)
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch season stage from Sofascore.")
            return None


    def get_team(self, team_id: str) -> Team | None:
        """ Fetch information about a specific team. """
        try:
            team_raw = self.provider.get_team(team_id=team_id)
            return Team.from_api(team_raw)
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch team from Sofascore.")
            return None

    def get_player(self, player_id: str) -> Player | None:
        """ Fetch information about a specific player. """
        try:
            player_raw = self.provider.get_player(player_id=player_id)
            return Player.from_api(player_raw)
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch player from Sofascore.")
            return None


    def get_manager(self, manager_id: str) -> Manager | None:
        """ Fetch information about a specific manager. """
        try:
            manager_raw = self.provider.get_manager(manager_id=manager_id)
            return Manager.from_api(manager_raw)
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch manager from Sofascore.")
            return None


    def get_referee(self, referee_id: str) -> Referee | None:
        """ Fetch information about a specific referee. """
        try:
            referee_raw = self.provider.get_referee(referee_id=referee_id)
            return Referee.from_api(referee_raw)
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch referee from Sofascore.")
            return None


    def get_venue(self, venue_id: str) -> Venue | None:
        """ Fetch information about a specific venue. """
        try:
            venue_raw = self.provider.get_venue(venue_id=venue_id)
            return Venue.from_api(venue_raw)
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch venue from Sofascore.")
            return None


    # ==================================================================
    # ===================== Event Oriented Queries =====================
    # ==================================================================

    def get_event(self, event_slug: str, event_id: str, event_custom_id: str) -> Event | None:
        """ Fetch information about a specific event. """
        try:
            event_raw = self.provider.get_event(event_slug=event_slug, event_id=event_id, event_custom_id=event_custom_id)
            return Event.from_api(event_raw)
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch event from Sofascore.")
            return None

    def get_lineups(self, event_id: str) -> Lineup | None:
        """ Fetch lineups for a specific event. """
        try:
            lineups_raw = self.provider.get_lineups(event_id=event_id)
            return Lineup.from_api(lineups_raw)
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch lineups from Sofascore.")
            return None


    def get_incidents(self, event_id: str) -> list[Incident]:
        """ Fetch incidents for a specific event. """
        try:
            incidents_raw = self.provider.get_incidents(event_id=event_id)
            return [Incident.from_api(incident) for incident in incidents_raw.get("incidents", [])]
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch incidents from Sofascore.")
            return []


    def get_events(self, date: str) -> list[Event]:
        """ Fetch all events scheduled for a specific date (format YYYY-MM-DD). """
        try:
            events_raw = self.provider.get_scheduled_events(sport=self.sport, date=date)
            return [Event.from_api(event) for event in events_raw.get("events", [])]
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch scheduled events from Sofascore.")
            return []

    def get_fixtures(
            self,
            *,
            unique_tournament_id: str | None = None,
            season_id: str | None = None,
            team_id: str | None = None,
            venue_id: str | None = None,
            page: int = 0,
        ) -> list[Event]:
        """ Fetch fixtures for a given target (tournament, team, or venue). """
        try:
            if unique_tournament_id is not None or season_id is not None:
                if not unique_tournament_id or not season_id:
                    raise ValueError("Both unique_tournament_id and season_id are required for fetching unique tournament fixtures.")
                fixtures_raw = self.provider.get_unique_tournament_fixtures(unique_tournament_id=unique_tournament_id, season_id=season_id, page=page)
            elif team_id is not None:
                if not team_id:
                    raise ValueError("team_id is required for fetching team fixtures.")
                fixtures_raw = self.provider.get_team_fixtures(team_id=team_id, page=page)
            elif venue_id is not None:
                if not venue_id:
                    raise ValueError("venue_id is required for fetching venue fixtures.")
                fixtures_raw = self.provider.get_venue_fixtures(venue_id=venue_id, page=page)
            else:
                raise ValueError("Invalid target for fetching fixtures. Must be 'unique-tournament', 'team', or 'venue'.")
            return [Event.from_api(event) for event in fixtures_raw.get("events", [])]
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch fixtures from Sofascore.")
            return []


    def get_results(
            self, 
            *,
            unique_tournament_id: str | None = None,
            season_id: str | None = None,
            team_id: str | None = None,
            venue_id: str | None = None,
            player_id: str | None = None,
            manager_id: str | None = None,
            referee_id: str | None = None,
            page: int = 0,
        ) -> list[Event]:
        """ Fetch results for a given target (tournament, team, player, manager, referee, or venue). """
        try:
            if unique_tournament_id is not None or season_id is not None:
                if not unique_tournament_id or not season_id:
                    raise ValueError("Both unique_tournament_id and season_id are required for fetching unique tournament results.")
                results_raw = self.provider.get_unique_tournament_results(unique_tournament_id=unique_tournament_id, season_id=season_id, page=page)
            elif team_id is not None:
                if not team_id:
                    raise ValueError("team_id is required for fetching team results.")
                results_raw = self.provider.get_team_results(team_id=team_id, page=page)
            elif player_id is not None:
                if not player_id:
                    raise ValueError("player_id is required for fetching player results.")
                results_raw = self.provider.get_player_results(player_id=player_id, page=page)
            elif manager_id is not None:
                if not manager_id:
                    raise ValueError("manager_id is required for fetching manager results.")
                results_raw = self.provider.get_manager_results(manager_id=manager_id, page=page)
            elif referee_id is not None:
                if not referee_id:
                    raise ValueError("referee_id is required for fetching referee results.")
                results_raw = self.provider.get_referee_results(referee_id=referee_id, page=page)
            elif venue_id is not None:
                if not venue_id:
                    raise ValueError("venue_id is required for fetching venue results.")
                results_raw = self.provider.get_venue_results(venue_id=venue_id, page=page)
            else:
                raise ValueError("Invalid target for fetching results. Must be 'unique-tournament', 'team', 'player', 'manager', or 'venue'.")
            return [Event.from_api(event) for event in results_raw.get("events", [])]
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch results from Sofascore.")
            return []


    def get_substages(self, stage_id: str) -> list[RoundStage]:
        """ Fetch substages for a specific stage. """
        try:
            substages_raw = self.provider.get_stage_substages(stage_id=stage_id)
            return [RoundStage.from_api(sub) for sub in substages_raw.get("stages", [])]
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch substages from Sofascore.")
            return []


    # ==================================================================
    # ==================== Ranking Oriented Queries ====================
    # ==================================================================

    def get_tournament_standings(self, unique_tournament_id: str | None = None, season_id: str | None = None, **kwargs) -> list[TeamStandings]:
        """ Fetch standings for a given unique tournament. """
        try:
            if not unique_tournament_id or not season_id:
                raise ValueError("Both unique_tournament_id and season_id are required for unique tournament standings.")
            standings_raw = self.provider.get_unique_tournament_standings(
                unique_tournament_id=unique_tournament_id,
                season_id=season_id,
                **kwargs
            ).get("standings", [{}])
            return [TeamStandings.from_api(std_raw) for std_raw in standings_raw]

        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch standings from Sofascore.")
            return []

    
    def get_stage_standings(self, target: Literal["constructors", "drivers"], season_stage_id: str) -> RacingStandings | None:
        """ Fetch standings for a given season stage (racing season). Target specifies whether to fetch constructor or driver standings. """
        try:
            if target == "constructors":
                standings_raw = self.provider.get_stage_standings_competitors(stage_id=season_stage_id)
            elif target == "drivers":
                standings_raw = self.provider.get_stage_standings_teams(stage_id=season_stage_id)
            else:
                raise ValueError("Invalid target for fetching standings. Must be 'unique-tournament', 'stage-constructors', or 'stage-drivers'.")
            return RacingStandings.from_api(standings_raw)
        except (RateLimitError, FetchError):
            logger.exception(f"Failed to fetch standings for target {target}.")
            return None


    def get_rankings(self, ranking_id: str) -> Rankings | None:
        """ Fetch a specific ranking by ID. """
        try:
            rankings_raw = self.provider.get_ranking(ranking_id=ranking_id)
            return Rankings.from_api(rankings_raw)
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch rankings from Sofascore.")
            return None


    # ==================================================================
    # ========================= Search Queries =========================
    # ==================================================================

    def search(
        self,
        target: Literal["unique-tournaments", "teams", "players", "managers", "referees", "venues", "events"],
        query: str,
        page: int = 0,
    ) -> list[UniqueTournament | Team | Player | Manager | Referee | Venue | Event]:
        """ Search for entities matching the query string. """
        search_mapping = {
            "unique-tournaments": self.provider.search_unique_tournaments,
            "teams": self.provider.search_teams,
            "players": self.provider.search_players,
            "managers": self.provider.search_managers,
            "referees": self.provider.search_referees,
            "venues": self.provider.search_venues,
            "events": self.provider.search_events,
        }
        entity_mapping: dict[str, BaseModel] = {
            "unique-tournaments": UniqueTournament,
            "teams": Team,
            "players": Player,
            "managers": Manager,
            "referees": Referee,
            "venues": Venue,
            "events": Event,
        }

        try:
            if target not in search_mapping:
                raise ValueError(f"Invalid search target: {target}. Must be one of {list(search_mapping.keys())}.")
            search_raw = search_mapping[target](query=query, page=page)
            entity_cls = entity_mapping[target]
            return [entity_cls.from_api(item) for item in search_raw.get("results", [])]
        except (RateLimitError, FetchError):
            logger.exception("Failed to perform search on Sofascore.")
            return []
