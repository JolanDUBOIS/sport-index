from datetime import datetime

from . import logger
from .fetcher import Fetcher
from .endpoints import ENDPOINTS
from .models import (
    Category,
    Channel,
    ChannelSchedule,
    CountryChannels,
    Event,
    Events,
    Incident,
    Lineups,
    Manager,
    Player,
    RacingStandings,
    Rankings,
    Referee,
    SearchResult,
    Season,
    Stage,
    Team,
    TeamPlayers,
    TeamStandings,
    UniqueStage,
    UniqueTournament,
    UniqueTournamentSeasons,
    Venue
)
from ..exceptions import NotFoundError


class SofascoreProvider():
    """ Raw data provider for Sofascore internal endpoints. """

    def __init__(self, fetch_delay: float = 0.5):
        self.fetcher = Fetcher()
        self.fetch_delay = fetch_delay

    # ---- Categories ---- #

    def get_categories(self, sport: str, raw: bool = False) -> list[Category] | dict:
        """ Fetch all categories for the sport. """
        logger.debug("Fetching all categories from Sofascore...")
        url = self._format("all-categories", sport=sport)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return [Category.from_api(cat) for cat in raw_data.get("categories", [])]

    def get_category_unique_tournaments(self, category_id: str, raw: bool = False) -> list[UniqueTournament] | dict:
        """ Fetch unique tournaments for a specific category. """
        logger.debug(f"Fetching unique tournaments for category ID: {category_id} from Sofascore...")
        url = self._format("category-unique-tournaments", category_id=category_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return [
            UniqueTournament.from_api(ut)
            for group in raw_data.get("groups", [])
            for ut in group.get("uniqueTournaments", [])
        ]

    def get_category_unique_stages(self, category_id: str, raw: bool = False) -> list[UniqueStage] | dict:
        """ Fetch unique stages for a specific category. """
        logger.debug(f"Fetching unique stages for category ID: {category_id} from Sofascore...")
        url = self._format("category-unique-stages", category_id=category_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return [UniqueStage.from_api(us) for us in raw_data.get("uniqueStages", [])]

    # ---- Unique Tournaments ---- #

    def get_unique_tournament(self, unique_tournament_id: str, raw: bool = False) -> UniqueTournament | dict:
        """ Fetch unique tournament details for a specific unique tournament ID. """
        logger.debug(f"Fetching details for unique tournament ID: {unique_tournament_id} from Sofascore...")
        url = self._format("unique-tournament", unique_tournament_id=unique_tournament_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return UniqueTournament.from_api(raw_data.get("uniqueTournament", {}))

    def get_unique_tournament_seasons(self, unique_tournament_id: str, raw: bool = False) -> list[Season] | dict:
        """ Fetch seasons for a specific unique tournament. """
        logger.debug(f"Fetching seasons for unique tournament ID: {unique_tournament_id} from Sofascore...")
        url = self._format("unique-tournament-seasons", unique_tournament_id=unique_tournament_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return [Season.from_api(season) for season in raw_data.get("seasons", [])]

    def get_unique_tournament_standings(self, unique_tournament_id: str, season_id: str, view: str = "total", raw: bool = False) -> list[TeamStandings] | dict:
        """ Fetch standings for a specific unique tournament and season. """
        logger.debug(f"Fetching standings for unique tournament ID: {unique_tournament_id}, season ID: {season_id} from Sofascore...")
        url = self._format("unique-tournament-standings", unique_tournament_id=unique_tournament_id, season_id=season_id, view=view)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return [TeamStandings.from_api(std) for std in raw_data.get("standings", [])]

    def get_unique_tournament_fixtures(self, unique_tournament_id: str, season_id: str, page: int = 0, raw: bool = False) -> Events | dict:
        """ Fetch upcoming fixtures for a specific unique tournament and season. """
        logger.debug(f"Fetching fixtures for unique tournament ID: {unique_tournament_id}, season ID: {season_id} from Sofascore...")
        url = self._format("unique-tournament-fixtures", unique_tournament_id=unique_tournament_id, season_id=season_id, page=page)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Events.from_api(raw_data)

    def get_unique_tournament_results(self, unique_tournament_id: str, season_id: str, page: int = 0, raw: bool = False) -> Events | dict:
        """ Fetch recent results for a specific unique tournament and season. """
        logger.debug(f"Fetching results for unique tournament ID: {unique_tournament_id}, season ID: {season_id} from Sofascore...")
        url = self._format("unique-tournament-results", unique_tournament_id=unique_tournament_id, season_id=season_id, page=page)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Events.from_api(raw_data)

    # ---- Teams ---- #

    def get_team(self, team_id: str, raw: bool = False) -> Team | dict:
        """ Fetch team details for a specific team ID. """
        logger.debug(f"Fetching details for team ID: {team_id} from Sofascore...")
        url = self._format("team", team_id=team_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Team.from_api(raw_data.get("team", {}))

    def get_team_seasons(self, team_id: str, raw: bool = False) -> list[UniqueTournamentSeasons] | dict:
        """ Fetch seasons for a specific team. """
        logger.debug(f"Fetching seasons for team ID: {team_id} from Sofascore...")
        url = self._format("team-seasons", team_id=team_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return [UniqueTournamentSeasons.from_api(uts) for uts in raw_data.get("uniqueTournamentSeasons", [])]

    def get_team_fixtures(self, team_id: str, page: int = 0, raw: bool = False) -> Events | dict:
        """ Fetch upcoming fixtures for a specific team. """
        logger.debug(f"Fetching fixtures for team ID: {team_id} from Sofascore...")
        url = self._format("team-fixtures", team_id=team_id, page=page)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Events.from_api(raw_data)

    def get_team_results(self, team_id: str, page: int = 0, raw: bool = False) -> Events | dict:
        """ Fetch recent results for a specific team. """
        logger.debug(f"Fetching results for team ID: {team_id} from Sofascore...")
        url = self._format("team-results", team_id=team_id, page=page)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Events.from_api(raw_data)

    def get_team_players(self, team_id: str, raw: bool = False) -> TeamPlayers | dict:
        """ Fetch players for a specific team. """
        logger.debug(f"Fetching players for team ID: {team_id} from Sofascore...")
        url = self._format("team-players", team_id=team_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return TeamPlayers.from_api(raw_data)

    def get_team_season_stats(self, team_id: str, unique_tournament_id: str, season_id: str) -> dict:
        """ Fetch season statistics for a specific team. """
        logger.debug(f"Fetching season stats for team ID: {team_id}, unique tournament ID: {unique_tournament_id}, season ID: {season_id} from Sofascore...")
        url = self._format("team-season-stats", team_id=team_id, unique_tournament_id=unique_tournament_id, season_id=season_id)
        return self.fetch_url(url)
        # TODO - Implement TeamSeasonStats model and return that instead of raw dict (careful, depending on type of tournament and sport, the stats returned can be very different - e.g. football vs basketball vs tennis)

    # ---- Players ---- #

    def get_player(self, player_id: str, raw: bool = False) -> Player | dict:
        """ Fetch player details for a specific player ID. """
        logger.debug(f"Fetching details for player ID: {player_id} from Sofascore...")
        url = self._format("player", player_id=player_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Player.from_api(raw_data.get("player", {}))

    def get_player_results(self, player_id: str, page: int = 0, raw: bool = False) -> Events | dict:
        """ Fetch recent results for a specific player. """
        logger.debug(f"Fetching results for player ID: {player_id} from Sofascore...")
        url = self._format("player-results", player_id=player_id, page=page)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Events.from_api(raw_data)

    def get_player_seasons(self, player_id: str, raw: bool = False) -> list[UniqueTournamentSeasons] | dict:
        """ Fetch seasons for a specific player. """
        logger.debug(f"Fetching seasons for player ID: {player_id} from Sofascore...")
        url = self._format("player-seasons", player_id=player_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return [UniqueTournamentSeasons.from_api(uts) for uts in raw_data.get("uniqueTournamentSeasons", [])]

    # ---- Managers ---- #

    def get_manager(self, manager_id: str, raw: bool = False) -> Manager | dict:
        """ Fetch manager details for a specific manager ID. """
        logger.debug(f"Fetching details for manager ID: {manager_id} from Sofascore...")
        url = self._format("manager", manager_id=manager_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Manager.from_api(raw_data.get("manager", {}))

    def get_manager_results(self, manager_id: str, page: int = 0, raw: bool = False) -> Events | dict:
        """ Fetch recent results for a specific manager. """
        logger.debug(f"Fetching results for manager ID: {manager_id} from Sofascore...")
        url = self._format("manager-results", manager_id=manager_id, page=page)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Events.from_api(raw_data)

    def get_manager_seasons(self, manager_id: str, raw: bool = False) -> list[UniqueTournamentSeasons] | dict:
        """ Fetch seasons for a specific manager. """
        logger.debug(f"Fetching seasons for manager ID: {manager_id} from Sofascore...")
        url = self._format("manager-seasons", manager_id=manager_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return [UniqueTournamentSeasons.from_api(uts) for uts in raw_data.get("uniqueTournamentSeasons", [])]

    # --- Referees ---- #

    def get_referee(self, referee_id: str, raw: bool = False) -> Referee | dict:
        """ Fetch referee details for a specific referee ID. """
        logger.debug(f"Fetching details for referee ID: {referee_id} from Sofascore...")
        url = self._format("referee", referee_id=referee_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Referee.from_api(raw_data.get("referee", {}))

    def get_referee_results(self, referee_id: str, page: int = 0, raw: bool = False) -> Events | dict:
        """ Fetch recent results for a specific referee. """
        logger.debug(f"Fetching results for referee ID: {referee_id} from Sofascore...")
        url = self._format("referee-results", referee_id=referee_id, page=page)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Events.from_api(raw_data)

    # ---- Venues ---- #

    def get_venue(self, venue_id: str, raw: bool = False) -> Venue | dict:
        """ Fetch venue details for a specific venue ID. """
        logger.debug(f"Fetching details for venue ID: {venue_id} from Sofascore...")
        url = self._format("venue", venue_id=venue_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Venue.from_api(raw_data.get("venue", {}))

    def get_venue_fixtures(self, venue_id: str, page: int = 1, raw: bool = False) -> Events | dict:
        """ Fetch upcoming fixtures for a specific venue. """
        logger.debug(f"Fetching fixtures for venue ID: {venue_id} from Sofascore...")
        url = self._format("venue-fixtures", venue_id=venue_id, page=page)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Events.from_api(raw_data)

    def get_venue_results(self, venue_id: str, page: int = 1, raw: bool = False) -> Events | dict:
        """ Fetch recent results for a specific venue. """
        logger.debug(f"Fetching results for venue ID: {venue_id} from Sofascore...")
        url = self._format("venue-results", venue_id=venue_id, page=page)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Events.from_api(raw_data)

    # ---- Events ---- #

    def get_event(self, event_id: str, raw: bool = False) -> Event | dict:
        """ Fetch event details for a specific event ID. """
        logger.debug(f"Fetching details for event ID: {event_id} from Sofascore...")
        url = self._format("event", event_id=event_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Event.from_api(raw_data.get("event", {}))

    def get_lineups(self, event_id: str, raw: bool = False) -> Lineups | dict:
        """ Fetch lineups for a specific event. """
        logger.debug(f"Fetching lineups for event ID: {event_id} from Sofascore...")
        url = self._format("event-lineups", event_id=event_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Lineups.from_api(raw_data.get("lineups", {}))

    def get_incidents(self, event_id: str, raw: bool = False) -> list[Incident] | dict:
        """ Fetch incidents for a specific event. """
        logger.debug(f"Fetching incidents for event ID: {event_id} from Sofascore...")
        url = self._format("event-incidents", event_id=event_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return [Incident.from_api(incident) for incident in raw_data.get("incidents", [])]

    def get_statistics(self, event_id: str) -> dict:
        """ Fetch statistics for a specific event. """
        logger.debug(f"Fetching statistics for event ID: {event_id} from Sofascore...")
        url = self._format("event-statistics", event_id=event_id)
        return self.fetch_url(url)
        # TODO

    def get_graph(self, event_id: str) -> dict:
        """ Fetch momentum graph for a specific event. """
        logger.debug(f"Fetching momentum graph for event ID: {event_id} from Sofascore...")
        url = self._format("event-graph", event_id=event_id)
        return self.fetch_url(url)
        # TODO

    def get_channels(self, event_id: str, raw: bool = False) -> CountryChannels | dict:
        """ Fetch channels for a specific event. """
        logger.debug(f"Fetching channels for event ID: {event_id} from Sofascore...")
        url = self._format("event-channels", event_id=event_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return CountryChannels._from_api(raw_data)

    def get_h2h_history(self, event_custom_id: str, raw: bool = False) -> Events | dict:
        """ Fetch head-to-head history for a specific event. """
        logger.debug(f"Fetching head-to-head history for event custom ID: {event_custom_id} from Sofascore...")
        url = self._format("event-h2h-history", event_custom_id=event_custom_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Events.from_api(raw_data)

    def get_scheduled_events(self, sport: str, date: str, raw: bool = False) -> Events | dict:
        """ Fetch scheduled events for a specific sport and date (format YYYY-MM-DD). """
        logger.debug(f"Fetching scheduled events for sport: {sport}, date: {date} from Sofascore...")
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            logger.error(f"Invalid date format: {date}. Expected format is YYYY-MM-DD.")
            raise ValueError(f"Invalid date format: {date}. Expected format is YYYY-MM-DD.")
        url = self._format("scheduled-events", sport=sport, date=date)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Events.from_api(raw_data)

    # ---- Rankings ---- #

    def get_ranking(self, ranking_id: str, raw: bool = False) -> Rankings | dict:
        """ Fetch a specific ranking by ID. """
        logger.debug(f"Fetching ranking ID: {ranking_id} from Sofascore...")
        url = self._format("ranking", ranking_id=ranking_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Rankings.from_api(raw_data)

    # --- Motorsport ---- #

    def get_unique_stage_seasons(self, unique_stage_id: str, raw: bool = False) -> list[Stage] | dict:
        """ Fetch seasons for a specific stage. """
        logger.debug(f"Fetching seasons for stage ID: {unique_stage_id} from Sofascore...")
        url = self._format("unique-stage-seasons", unique_stage_id=unique_stage_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return [Stage._from_api(stage) for stage in raw_data.get("seasons", [])]

    def get_stage(self, stage_id: str, raw: bool = False) -> Stage | dict: # NOTE - Irrelevant as get_stage_details returns the same details & more
        """ Fetch stage details for a specific stage ID. """
        logger.debug(f"Fetching details for stage ID: {stage_id} from Sofascore...")
        url = self._format("stage", stage_id=stage_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Stage.from_api(raw_data.get("stage", {}))

    def get_stage_substages(self, stage_id: str, raw: bool = False) -> list[Stage] | dict: # NOTE - Irrelevant as get_stage_details returns the same details & more
        """ Fetch substages for a specific stage. """
        logger.debug(f"Fetching substages for stage ID: {stage_id} from Sofascore...")
        url = self._format("substages", stage_id=stage_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return [Stage.from_api(stage) for stage in raw_data.get("stages", [])]

    def get_stage_details(self, stage_id: str, raw: bool = False) -> Stage | dict:
        """ Fetch extended details for a specific stage, including nested substages. """
        logger.debug(f"Fetching extended details for stage ID: {stage_id} from Sofascore...")
        url = self._format("stage-details", stage_id=stage_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return Stage.from_api(raw_data.get("stage", {}))

    def get_stage_standings_competitors(self, stage_id: str, raw: bool = False) -> RacingStandings | dict:
        """ Fetch competitor (aka constructor or racing team) standings for a specific stage. """
        logger.debug(f"Fetching competitor standings for stage ID: {stage_id} from Sofascore...")
        url = self._format("standings-competitors", stage_id=stage_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return RacingStandings.from_api({"kind": "competitors", "standings": raw_data.get("standings", [])})

    def get_stage_standings_teams(self, stage_id: str, raw: bool = False) -> RacingStandings | dict:
        """ Fetch team standings (aka driver) for a specific stage. """
        logger.debug(f"Fetching team standings for stage ID: {stage_id} from Sofascore...")
        url = self._format("standings-teams", stage_id=stage_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return RacingStandings.from_api({"kind": "teams", "standings": raw_data.get("standings", [])})

    # ---- TV Channels ---- #

    def get_country_channels(self, country_code: str, raw: bool = False) -> list[Channel] | dict:
        """ Fetch TV channels for a specific country code. """
        logger.debug(f"Fetching TV channels for country code: {country_code} from Sofascore...")
        url = self._format("country-channels", country_code=country_code)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return [Channel._from_api(channel) for channel in raw_data.get("channels", [])]

    def get_channel_schedule(self, channel_id: str, raw: bool = False) -> ChannelSchedule | dict:
        """ Fetch schedule for a specific TV channel. """
        logger.debug(f"Fetching schedule for channel ID: {channel_id} from Sofascore...")
        url = self._format("channel-schedule", channel_id=channel_id)
        raw_data = self.fetch_url(url)
        if raw:
            return raw_data
        return ChannelSchedule._from_api(raw_data)

    # ---- Search ---- #

    def search_all(self, query: str, page: int = 0, raw: bool = False) -> list[SearchResult] | dict:
        """ Search for all entities by name. """
        logger.debug(f"Searching for all entities with query: '{query}' on Sofascore...")
        url = self._format("search-all")
        params = {"q": query, "page": page}
        raw_data = self.fetch_url(url, params=params, fetch_delay=0)
        if raw:
            return raw_data
        return [SearchResult._from_api(result) for result in raw_data.get("results", [])]

    def search_unique_tournaments(self, query: str, page: int = 0, raw: bool = False) -> list[SearchResult] | dict:
        """ Search for unique tournaments by name. """
        logger.debug(f"Searching for unique tournaments with query: '{query}' on Sofascore...")
        url = self._format("search-unique-tournaments")
        params = {"q": query, "page": page}
        raw_data = self.fetch_url(url, params=params, fetch_delay=0)
        if raw:
            return raw_data
        return [SearchResult._from_api(result) for result in raw_data.get("results", [])]

    def search_teams(self, query: str, page: int = 0, raw: bool = False) -> list[SearchResult] | dict:
        """ Search for teams by name. """
        logger.debug(f"Searching for teams with query: '{query}' on Sofascore...")
        url = self._format("search-teams")
        params = {"q": query, "page": page}
        raw_data = self.fetch_url(url, params=params, fetch_delay=0)
        if raw:
            return raw_data
        return [SearchResult._from_api(result) for result in raw_data.get("results", [])]

    def search_events(self, query: str, page: int = 0, raw: bool = False) -> list[SearchResult] | dict:
        """ Search for events by name. """
        logger.debug(f"Searching for events with query: '{query}' on Sofascore...")
        url = self._format("search-events")
        params = {"q": query, "page": page}
        raw_data = self.fetch_url(url, params=params, fetch_delay=0)
        if raw:
            return raw_data
        return [SearchResult._from_api(result) for result in raw_data.get("results", [])]

    def search_players(self, query: str, page: int = 0, raw: bool = False) -> list[SearchResult] | dict:
        """ Search for players by name. """
        logger.debug(f"Searching for players with query: '{query}' on Sofascore...")
        url = self._format("search-players")
        params = {"q": query, "page": page}
        raw_data = self.fetch_url(url, params=params, fetch_delay=0)
        if raw:
            return raw_data
        return [SearchResult._from_api(result) for result in raw_data.get("results", [])]

    def search_managers(self, query: str, page: int = 0, raw: bool = False) -> list[SearchResult] | dict:
        """ Search for managers by name. """
        logger.debug(f"Searching for managers with query: '{query}' on Sofascore...")
        url = self._format("search-managers")
        params = {"q": query, "page": page}
        raw_data = self.fetch_url(url, params=params, fetch_delay=0)
        if raw:
            return raw_data
        return [SearchResult._from_api(result) for result in raw_data.get("results", [])]

    def search_referees(self, query: str, page: int = 0, raw: bool = False) -> list[SearchResult] | dict:
        """ Search for referees by name. """
        logger.debug(f"Searching for referees with query: '{query}' on Sofascore...")
        url = self._format("search-referees")
        params = {"q": query, "page": page}
        raw_data = self.fetch_url(url, params=params, fetch_delay=0)
        if raw:
            return raw_data
        return [SearchResult._from_api(result) for result in raw_data.get("results", [])]

    def search_venues(self, query: str, page: int = 0, raw: bool = False) -> list[SearchResult] | dict:
        """ Search for venues by name. """
        logger.debug(f"Searching for venues with query: '{query}' on Sofascore...")
        url = self._format("search-venues")
        params = {"q": query, "page": page}
        raw_data = self.fetch_url(url, params=params, fetch_delay=0)
        if raw:
            return raw_data
        return [SearchResult._from_api(result) for result in raw_data.get("results", [])]

    # ---- Helpers ---- #

    def _format(self, endpoint_name: str, **kwargs) -> str:
        """ Helper method to format endpoint URLs. """
        if endpoint_name not in ENDPOINTS:
            logger.error(f"Endpoint '{endpoint_name}' not found in ENDPOINTS.")
            raise ValueError(f"Endpoint '{endpoint_name}' is not defined.")
        return ENDPOINTS[endpoint_name].format(**kwargs)

    def fetch_url(self, url: str, *, params: dict = None, fetch_delay: float = None) -> dict:
        try:
            response = self.fetcher.fetch_url(url, params=params, initial_delay=fetch_delay or self.fetch_delay)
        except NotFoundError:
            return {}
        return response.json()
