from typing import Literal

from . import logger
from .provider import SofascoreProvider
from .transformers import (
    transform_category,
    transform_competition,
    transform_event,
    transform_lineups,
    transform_manager,
    transform_player,
    transform_referee,
    transform_rankings,
    transform_search_results,
    transform_season,
    transform_standings,
    transform_team,
    transform_venue,
)
from sportindex.core import RateLimitError, FetchError


class Client:
    """ TODO """

    def __init__(self, sport: str, **kwargs):
        self.sport = sport
        self.provider = SofascoreProvider(sport=sport, **kwargs)


    # ==================================================================
    # =================== Discovery Oriented Queries ===================
    # ==================================================================

    def get_categories(self) -> dict:
        """ Fetch all categories for the sport. """
        try:
            categories_raw = self.provider.get_categories()
            categories = [transform_category(cat) for cat in categories_raw.get("categories", [])]
            return {"categories": categories, "query": {}}
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch categories from Sofascore.")
            return {"categories": [], "query": {}}


    def get_competitions(self, category_id: str) -> dict:
        """ Fetch all competitions for a given category. """
        query = {"category_id": category_id}
        try:
            competitions_raw = self.provider.get_category_competitions(category_id=category_id)
            groups = competitions_raw.get("groups", [])
            if not groups or not isinstance(groups, list) or not isinstance(groups[0], dict):
                return {"competitions": [], "query": query}

            competitions = [transform_competition(comp) for comp in groups[0].get("uniqueTournaments", [])]
            return {"competitions": competitions, "query": query}
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch competitions from Sofascore.")
            return {"competitions": [], "query": query}


    def get_seasons(
        self,
        target: Literal["competition", "team"],
        *,
        competition_id: str | None = None,
        team_id: str | None = None,
    ) -> dict:
        """ Fetch seasons for a given competition. """
        query = {"competition_id": competition_id}
        try:
            if target == "competition":
                if not competition_id:
                    raise ValueError("competition_id is required for fetching competition seasons.")
                seasons_raw = self.provider.get_competition_seasons(competition_id=competition_id)
            elif target == "team":
                if not team_id:
                    raise ValueError("team_id is required for fetching team seasons.")
                seasons_raw = self.provider.get_team_seasons(team_id=team_id)
            else:
                raise ValueError("Invalid target for fetching seasons. Must be 'competition' or 'team'.")
            seasons = [transform_season(season) for season in seasons_raw.get("seasons", [])]
            return {"seasons": seasons, "query": query}
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch seasons from Sofascore.")
            return {"seasons": [], "query": query}


    # ==================================================================
    # ===================== Entity Oriented Queries ====================
    # ==================================================================

    def get_competition(self, competition_id: str) -> dict:
        """ Fetch information about a specific competition. """
        query = {"competition_id": competition_id}
        try:
            competition_raw = self.provider.get_competition(competition_id=competition_id)
            competition = transform_competition(competition_raw)
            return {"competition": competition, "query": query}
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch competition from Sofascore.")
            return {"competition": None, "query": query}


    def get_team(self, team_id: str) -> dict:
        """ Fetch information about a specific team. """
        query = {"team_id": team_id}
        try:
            team_raw = self.provider.get_team(team_id=team_id)
            team = transform_team(team_raw)
            return {"team": team, "query": query}
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch team from Sofascore.")
            return {"team": None, "query": query}


    def get_player(self, player_id: str) -> dict:
        """ Fetch information about a specific player. """
        query = {"player_id": player_id}
        try:
            player_raw = self.provider.get_player(player_id=player_id)
            player = transform_player(player_raw)
            return {"player": player, "query": query}
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch player from Sofascore.")
            return {"player": None, "query": query}


    def get_manager(self, manager_id: str) -> dict:
        """ Fetch information about a specific manager. """
        query = {"manager_id": manager_id}
        try:
            manager_raw = self.provider.get_manager(manager_id=manager_id)
            manager = transform_manager(manager_raw)
            return {"manager": manager, "query": query}
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch manager from Sofascore.")
            return {"manager": None, "query": query}


    def get_referee(self, referee_id: str) -> dict:
        """ Fetch information about a specific referee. """
        query = {"referee_id": referee_id}
        try:
            referee_raw = self.provider.get_referee(referee_id=referee_id)
            referee = transform_referee(referee_raw)
            return {"referee": referee, "query": query}
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch referee from Sofascore.")
            return {"referee": None, "query": query}


    def get_venue(self, venue_id: str) -> dict:
        """ Fetch information about a specific venue. """
        query = {"venue_id": venue_id}
        try:
            venue_raw = self.provider.get_venue(venue_id=venue_id)
            venue = transform_venue(venue_raw)
            return {"venue": venue, "query": query}
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch venue from Sofascore.")
            return {"venue": None, "query": query}


    # ==================================================================
    # ===================== Event Oriented Queries =====================
    # ==================================================================

    def get_event(self, event_slug: str, event_id: str, event_custom_id: str) -> dict:
        """ Fetch information about a specific event. """
        query = {"event_slug": event_slug, "event_id": event_id, "event_custom_id": event_custom_id}
        try:
            event_raw = self.provider.get_event(event_slug=event_slug, event_id=event_id, event_custom_id=event_custom_id)
            event = transform_event(event_raw)
            return {"event": event, "query": query}
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch event from Sofascore.")
            return {"event": None, "query": query}


    def get_lineups(self, event_id: str) -> dict:
        """ Fetch lineups for a specific event. """
        query = {"event_id": event_id}
        try:
            lineups_raw = self.provider.get_lineups(event_id=event_id)
            lineups = transform_lineups(lineups_raw)
            return {"lineups": lineups, "query": query}
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch lineups from Sofascore.")
            return {"lineups": None, "query": query}


    def get_fixtures(
            self, 
            target: Literal["competition", "team", "venue"],
            *,
            competition_id: str = None,
            season_id: str = None,
            team_id: str = None,
            venue_id: str = None,
            page: int = 0,
        ) -> dict:
        """ Fetch fixtures for a given target (competition or team). """
        query = {"target": target, "competition_id": competition_id, "season_id": season_id, "team_id": team_id, "venue_id": venue_id, "page": page}
        try:
            if target == "competition":
                if not competition_id or not season_id:
                    raise ValueError("Both competition_id and season_id are required for fetching competition fixtures.")
                fixtures_raw = self.provider.get_competition_fixtures(competition_id=competition_id, season_id=season_id, page=page)
            elif target == "team":
                if not team_id:
                    raise ValueError("team_id is required for fetching team fixtures.")
                fixtures_raw = self.provider.get_team_fixtures(team_id=team_id, page=page)
            elif target == "venue":
                if not venue_id:
                    raise ValueError("venue_id is required for fetching venue fixtures.")
                fixtures_raw = self.provider.get_venue_fixtures(venue_id=venue_id, page=page)
            else:
                raise ValueError("Invalid target for fetching fixtures. Must be 'competition', 'team', or 'venue'.")

            events = fixtures_raw.get("events", [])
            fixtures = [transform_event(event) for event in events]
            return {"fixtures": fixtures, "has_next_page": fixtures_raw.get("hasNextPage", False), "query": query}

        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch fixtures from Sofascore.")
            return {"fixtures": [], "has_next_page": False, "query": query}


    def get_results(
            self, 
            target: Literal["competition", "team", "player", "manager", "referee", "venue"],
            *,
            competition_id: str = None,
            season_id: str = None,
            team_id: str = None,
            venue_id: str = None,
            player_id: str = None,
            manager_id: str = None,
            referee_id: str = None,
            page: int = 0,
        ) -> dict:
        """ Fetch results for a given target (competition or team). """
        query = {"target": target, "competition_id": competition_id, "season_id": season_id, "team_id": team_id, "venue_id": venue_id, "player_id": player_id, "manager_id": manager_id, "page": page}
        try:
            if target == "competition":
                if not competition_id or not season_id:
                    raise ValueError("Both competition_id and season_id are required for fetching competition results.")
                results_raw = self.provider.get_competition_results(competition_id=competition_id, season_id=season_id, page=page)
            elif target == "team":
                if not team_id:
                    raise ValueError("team_id is required for fetching team results.")
                results_raw = self.provider.get_team_results(team_id=team_id, page=page)
            elif target == "player":
                if not player_id:
                    raise ValueError("player_id is required for fetching player results.")
                results_raw = self.provider.get_player_results(player_id=player_id, page=page)
            elif target == "manager":
                if not manager_id:
                    raise ValueError("manager_id is required for fetching manager results.")
                results_raw = self.provider.get_manager_results(manager_id=manager_id, page=page)
            elif target == "referee":
                if not referee_id:
                    raise ValueError("referee_id is required for fetching referee results.")
                results_raw = self.provider.get_referee_results(referee_id=referee_id, page=page)
            elif target == "venue":
                if not venue_id:
                    raise ValueError("venue_id is required for fetching venue results.")
                results_raw = self.provider.get_venue_results(venue_id=venue_id, page=page)
            else:
                raise ValueError("Invalid target for fetching results. Must be 'competition', 'team', 'player', 'manager', or 'venue'.")

            events = results_raw.get("events", [])
            results = [transform_event(event) for event in events]
            return {"results": results, "has_next_page": results_raw.get("hasNextPage", False), "query": query}

        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch results from Sofascore.")
            return {"results": [], "has_next_page": False, "query": query}


    # ==================================================================
    # ==================== Ranking Oriented Queries ====================
    # ==================================================================

    def get_standings(self, competition_id: str, season_id: str, **kwargs) -> dict:
        """ Fetch standings for a given competition and season. """
        query = {"competition_id": competition_id, "season_id": season_id}
        try:
            standings_raw = self.provider.get_competition_standings(
                competition_id=competition_id,
                season_id=season_id,
                **kwargs
            ).get("standings", [{}])
            return {"standings": [
                    transform_standings(std_raw)
                    for std_raw in standings_raw
                ],
                "query": query
            }

        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch standings from Sofascore.")
            return {"standings": [], "query": query}


    def get_rankings(self, ranking_id: str) -> dict:
        """ Fetch a specific ranking by ID. """
        query = {"ranking_id": ranking_id}
        try:
            rankings_raw = self.provider.get_ranking(ranking_id=ranking_id)
            rankings = transform_rankings(rankings_raw)
            return {"rankings": rankings, "query": query}
        except (RateLimitError, FetchError):
            logger.exception("Failed to fetch rankings from Sofascore.")
            return {"rankings": [], "query": query}


    # ==================================================================
    # ========================= Search Queries =========================
    # ==================================================================

    def search(
        self,
        target: Literal["competitions", "teams", "players", "managers", "referees", "venues", "events"],
        query: str,
        page: int = 0,
    ) -> dict:
        """ Search for entities matching the query string. """
        search_mapping = {
            "competitions": self.provider.search_competitions,
            "teams": self.provider.search_teams,
            "players": self.provider.search_players,
            "managers": self.provider.search_managers,
            "referees": self.provider.search_referees,
            "venues": self.provider.search_venues,
            "events": self.provider.search_events,
        }

        query_info = {"target": target, "query": query, "page": page}
        try:
            if target not in search_mapping:
                raise ValueError(f"Invalid search target: {target}. Must be one of {list(search_mapping.keys())}.")
            search_raw = search_mapping[target](query=query, page=page)
            search_results = transform_search_results(target=target, raw=search_raw)
            return {**search_results, "query": query_info}
        except (RateLimitError, FetchError):
            logger.exception("Failed to perform search on Sofascore.")
            return {target: [], "query": query_info}
