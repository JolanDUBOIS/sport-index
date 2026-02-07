from requests import Response

from . import logger
from .endpoints import ENDPOINTS
from sportindex.core import Fetcher


class SofascoreProvider():
    """ Raw data provider for Sofascore internal endpoints. """

    def __init__(self, fetch_delay: float = 0.5, **kwargs):
        self.fetcher = Fetcher()
        self.fetch_delay = fetch_delay

    # ---- Categories ---- #

    def get_categories(self, sport: str) -> dict:
        """ Fetch all categories for the sport. """
        logger.info("Fetching all categories from Sofascore...")
        url = self._format("all-categories", sport=sport)
        return self.fetch_url(url)

    def get_category_competitions(self, category_id: str) -> dict:
        """ Fetch competitions for a specific category. """
        logger.info(f"Fetching competitions for category ID: {category_id} from Sofascore...")
        url = self._format("category-competitions", category_id=category_id)
        return self.fetch_url(url)

    # ---- Competitions ---- #

    def get_competition(self, competition_id: str) -> dict:
        """ Fetch competition details for a specific competition ID. """
        logger.info(f"Fetching details for competition ID: {competition_id} from Sofascore...")
        url = self._format("competition", competition_id=competition_id)
        return self.fetch_url(url)

    def get_competition_seasons(self, competition_id: str) -> dict:
        """ Fetch seasons for a specific competition. """
        logger.info(f"Fetching seasons for competition ID: {competition_id} from Sofascore...")
        url = self._format("competition-seasons", competition_id=competition_id)
        return self.fetch_url(url)

    def get_competition_standings(self, competition_id: str, season_id: str, view: str = "total") -> dict:
        """ Fetch standings for a specific competition and season. """
        logger.info(f"Fetching standings for competition ID: {competition_id}, season ID: {season_id} from Sofascore...")
        url = self._format("competition-standings", competition_id=competition_id, season_id=season_id, view=view)
        return self.fetch_url(url)

    def get_competition_fixtures(self, competition_id: str, season_id: str, page: int = 0) -> dict:
        """ Fetch upcoming fixtures for a specific competition and season. """
        logger.info(f"Fetching fixtures for competition ID: {competition_id}, season ID: {season_id} from Sofascore...")
        url = self._format("competition-fixtures", competition_id=competition_id, season_id=season_id, page=page)
        return self.fetch_url(url)

    def get_competition_results(self, competition_id: str, season_id: str, page: int = 0) -> dict:
        """ Fetch recent results for a specific competition and season. """
        logger.info(f"Fetching results for competition ID: {competition_id}, season ID: {season_id} from Sofascore...")
        url = self._format("competition-results", competition_id=competition_id, season_id=season_id, page=page)
        return self.fetch_url(url)

    # ---- Teams ---- #

    def get_team(self, team_id: str) -> dict:
        """ Fetch team details for a specific team ID. """
        logger.info(f"Fetching details for team ID: {team_id} from Sofascore...")
        url = self._format("team", team_id=team_id)
        return self.fetch_url(url)

    def get_team_players(self, team_id: str) -> dict:
        """ Fetch players for a specific team. """
        logger.info(f"Fetching players for team ID: {team_id} from Sofascore...")
        url = self._format("team-players", team_id=team_id)
        return self.fetch_url(url)

    def get_team_fixtures(self, team_id: str, page: int = 0) -> dict:
        """ Fetch upcoming fixtures for a specific team. """
        logger.info(f"Fetching fixtures for team ID: {team_id} from Sofascore...")
        url = self._format("team-fixtures", team_id=team_id, page=page)
        return self.fetch_url(url)

    def get_team_results(self, team_id: str, page: int = 0) -> dict:
        """ Fetch recent results for a specific team. """
        logger.info(f"Fetching results for team ID: {team_id} from Sofascore...")
        url = self._format("team-results", team_id=team_id, page=page)
        return self.fetch_url(url)

    def get_team_seasons(self, team_id: str) -> dict:
        """ Fetch seasons for a specific team. """
        logger.info(f"Fetching seasons for team ID: {team_id} from Sofascore...")
        url = self._format("team-seasons", team_id=team_id)
        return self.fetch_url(url)

    def get_team_year_stats(self, team_id: str, year: int) -> dict:
        """ Fetch yearly statistics for a specific team. """
        logger.info(f"Fetching yearly stats for team ID: {team_id}, year: {year} from Sofascore...")
        url = self._format("team-year-stats", team_id=team_id, year=year)
        return self.fetch_url(url)

    # ---- Players ---- #

    def get_player(self, player_id: str) -> dict:
        """ Fetch player details for a specific player ID. """
        logger.info(f"Fetching details for player ID: {player_id} from Sofascore...")
        url = self._format("player", player_id=player_id)
        return self.fetch_url(url)

    def get_player_results(self, player_id: str, page: int = 0) -> dict:
        """ Fetch recent results for a specific player. """
        logger.info(f"Fetching results for player ID: {player_id} from Sofascore...")
        url = self._format("player-results", player_id=player_id, page=page)
        return self.fetch_url(url)

    def get_player_seasons(self, player_id: str) -> dict:
        """ Fetch seasons for a specific player. """
        logger.info(f"Fetching seasons for player ID: {player_id} from Sofascore...")
        url = self._format("player-seasons", player_id=player_id)
        return self.fetch_url(url)

    # ---- Managers ---- #

    def get_manager(self, manager_id: str) -> dict:
        """ Fetch manager details for a specific manager ID. """
        logger.info(f"Fetching details for manager ID: {manager_id} from Sofascore...")
        url = self._format("manager", manager_id=manager_id)
        return self.fetch_url(url)

    def get_manager_results(self, manager_id: str, page: int = 0) -> dict:
        """ Fetch recent results for a specific manager. """
        logger.info(f"Fetching results for manager ID: {manager_id} from Sofascore...")
        url = self._format("manager-results", manager_id=manager_id, page=page)
        return self.fetch_url(url)

    def get_manager_seasons(self, manager_id: str) -> dict:
        """ Fetch seasons for a specific manager. """
        logger.info(f"Fetching seasons for manager ID: {manager_id} from Sofascore...")
        url = self._format("manager-seasons", manager_id=manager_id)
        return self.fetch_url(url)

    # --- Referees ---- #

    def get_referee(self, referee_id: str) -> dict:
        """ Fetch referee details for a specific referee ID. """
        logger.info(f"Fetching details for referee ID: {referee_id} from Sofascore...")
        url = self._format("referee", referee_id=referee_id)
        return self.fetch_url(url)

    def get_referee_results(self, referee_id: str, page: int = 0) -> dict:
        """ Fetch recent results for a specific referee. """
        logger.info(f"Fetching results for referee ID: {referee_id} from Sofascore...")
        url = self._format("referee-results", referee_id=referee_id, page=page)
        return self.fetch_url(url)

    # ---- Venues ---- #

    def get_venue(self, venue_id: str) -> dict:
        """ Fetch venue details for a specific venue ID. """
        logger.info(f"Fetching details for venue ID: {venue_id} from Sofascore...")
        url = self._format("venue", venue_id=venue_id)
        return self.fetch_url(url)

    def get_venue_fixtures(self, venue_id: str, page: int = 1) -> dict:
        """ Fetch upcoming fixtures for a specific venue. """
        logger.info(f"Fetching fixtures for venue ID: {venue_id} from Sofascore...")
        url = self._format("venue-fixtures", venue_id=venue_id, page=page)
        return self.fetch_url(url)

    def get_venue_results(self, venue_id: str, page: int = 1) -> dict:
        """ Fetch recent results for a specific venue. """
        logger.info(f"Fetching results for venue ID: {venue_id} from Sofascore...")
        url = self._format("venue-results", venue_id=venue_id, page=page)
        return self.fetch_url(url)

    # ---- Events ---- #

    def get_event(self, event_id: str) -> dict:
        """ Fetch event details for a specific event ID. """
        logger.info(f"Fetching details for event ID: {event_id} from Sofascore...")
        url = self._format("event", event_id=event_id)
        return self.fetch_url(url)

    def get_lineups(self, event_id: str) -> dict:
        """ Fetch lineups for a specific event. """
        logger.info(f"Fetching lineups for event ID: {event_id} from Sofascore...")
        url = self._format("lineups", event_id=event_id)
        return self.fetch_url(url)

    def get_h2h_history(self, event_custom_id: str) -> dict:
        """ Fetch head-to-head history for a specific event. """
        logger.info(f"Fetching head-to-head history for event custom ID: {event_custom_id} from Sofascore...")
        url = self._format("h2h-history", event_custom_id=event_custom_id)
        return self.fetch_url(url)

    # ---- Rankings ---- #

    def get_ranking(self, ranking_id: str) -> dict:
        """ Fetch a specific ranking by ID. """
        logger.info(f"Fetching ranking ID: {ranking_id} from Sofascore...")
        url = self._format("ranking", ranking_id=ranking_id)
        return self.fetch_url(url)

    # ---- Search ---- #

    def search_competitions(self, query: str, page: int = 0) -> dict:
        """ Search for competitions by name. """
        logger.debug(f"Searching for competitions with query: '{query}' on Sofascore...")
        url = self._format("search-competitions")
        params = {"q": query, "page": page}
        return self.fetch_url(url, params=params, fetch_delay=0)

    def search_teams(self, query: str, page: int = 0) -> dict:
        """ Search for teams by name. """
        logger.debug(f"Searching for teams with query: '{query}' on Sofascore...")
        url = self._format("search-teams")
        params = {"q": query, "page": page}
        return self.fetch_url(url, params=params, fetch_delay=0)

    def search_events(self, query: str, page: int = 0) -> dict:
        """ Search for events by name. """
        logger.debug(f"Searching for events with query: '{query}' on Sofascore...")
        url = self._format("search-events")
        params = {"q": query, "page": page}
        return self.fetch_url(url, params=params, fetch_delay=0)

    def search_players(self, query: str, page: int = 0) -> dict:
        """ Search for players by name. """
        logger.debug(f"Searching for players with query: '{query}' on Sofascore...")
        url = self._format("search-players")
        params = {"q": query, "page": page}
        return self.fetch_url(url, params=params, fetch_delay=0)

    def search_managers(self, query: str, page: int = 0) -> dict:
        """ Search for managers by name. """
        logger.debug(f"Searching for managers with query: '{query}' on Sofascore...")
        url = self._format("search-managers")
        params = {"q": query, "page": page}
        return self.fetch_url(url, params=params, fetch_delay=0)

    def search_referees(self, query: str, page: int = 0) -> dict:
        """ Search for referees by name. """
        logger.debug(f"Searching for referees with query: '{query}' on Sofascore...")
        url = self._format("search-referees")
        params = {"q": query, "page": page}
        return self.fetch_url(url, params=params, fetch_delay=0)

    def search_venues(self, query: str, page: int = 0) -> dict:
        """ Search for venues by name. """
        logger.debug(f"Searching for venues with query: '{query}' on Sofascore...")
        url = self._format("search-venues")
        params = {"q": query, "page": page}
        return self.fetch_url(url, params=params, fetch_delay=0)

    # ---- Helpers ---- #

    def _format(self, endpoint_name: str, **kwargs) -> str:
        """ Helper method to format endpoint URLs. """
        if endpoint_name not in ENDPOINTS:
            logger.error(f"Endpoint '{endpoint_name}' not found in ENDPOINTS.")
            raise ValueError(f"Endpoint '{endpoint_name}' is not defined.")
        return ENDPOINTS[endpoint_name].format(**kwargs)

    def fetch_url(self, url: str, *, params: dict = None, raw: bool = False, fetch_delay: float = None) -> dict | Response:
        response = self.fetcher.fetch_url(url, params=params, initial_delay=fetch_delay or self.fetch_delay)
        if raw:
            return response
        return response.json()
