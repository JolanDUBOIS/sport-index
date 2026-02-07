# import string
# import json

# from bs4 import BeautifulSoup

# from . import logger
# from .endpoints import ENDPOINTS
# from sportindex.core import BaseProvider, FetchError


# class OneFootballProvider(BaseProvider):
#     """ Raw data provider for OneFootball internal endpoints. """

#     def __init__(self, build_id: str = None, language: str = "en", **kwargs):
#         super().__init__(**kwargs)
#         self.language = language
#         self.build_id = build_id or self.fetch_build_id()

#     def fetch_build_id(self) -> str:
#         """ Fetch the current build ID from OneFootball homepage. """
#         logger.info("Fetching current OneFootball build ID...")
#         url = ENDPOINTS["main-page"].format(language=self.language)

#         response = self.fetcher.fetch_url(url, initial_delay=self.fetch_delay)
#         soup = BeautifulSoup(response.text, 'html.parser')

#         script = soup.find('script', id="__NEXT_DATA__")
#         if not script:
#             logger.error("Failed to find __NEXT_DATA__ script tag on OneFootball homepage.")
#             raise FetchError("Could not find build ID on OneFootball homepage.")

#         data = json.loads(script.string)
#         return data['buildId']

#     # ---- Competitions ---- #

#     def get_all_competitions(self) -> dict:
#         """ Fetch competitions listed on OneFootball. """
#         logger.info("Fetching competitions list from OneFootball...")
#         competitions = {}

#         for letter in string.ascii_lowercase:
#             try:
#                 competitions[letter] = self._get_all_competitions_letter(letter)
#             except FetchError:
#                 logger.debug(f"Failed to fetch competitions for letter '{letter}'. Continuing with next letter.")
#                 continue
        
#         return {"competitions": competitions}

#     def _get_all_competitions_letter(self, letter: str) -> dict:
#         """ Fetch competitions for a specific starting letter. """
#         logger.info(f"Fetching competitions starting with letter '{letter.capitalize()}'...")
#         url = self._format("all-competitions", letter=letter)

#         return self.fetch_url(url)

#     def get_competition_standings(self, competition_id: str) -> dict:
#         """ Fetch standings for a specific competition. """
#         logger.info(f"Fetching standings for competition: {competition_id} from OneFootball...")
#         url = self._format("competition-standings", competition_id=competition_id)

#         data = self.fetch_url(url)

#         return {"standings": data}

#     def get_competition_fixtures(self, competition_id: str) -> dict:
#         """ Fetch fixtures for a specific competition. """
#         logger.info(f"Fetching fixtures for competition: {competition_id} from OneFootball...")
#         url = self._format("competition-fixtures", competition_id=competition_id)

#         data = self.fetch_url(url)

#         return {"fixtures": data}

#     def get_competition_results(self, competition_id: str) -> dict:
#         """ Fetch results for a specific competition. """
#         logger.info(f"Fetching results for competition: {competition_id} from OneFootball...")
#         url = self._format("competition-results", competition_id=competition_id)

#         data = self.fetch_url(url)

#         return {"results": data}
    
#     # ---- Teams ---- #

#     def get_all_teams(self) -> dict:
#         """ Fetch all teams listed on OneFootball. """
#         logger.info("Fetching all teams from OneFootball...")
#         logger.info("This may take a while as teams are fetched letter by letter, page by page...")
#         teams = {}

#         for letter in string.ascii_lowercase:
#             try:
#                 teams[letter] = self._get_all_teams_letter(letter)
#             except FetchError:
#                 logger.debug(f"Failed to fetch teams for letter '{letter}'. Continuing with next letter.")
#                 continue

#         return {"teams": teams}

#     def _get_all_teams_letter(self, letter: str) -> dict:
#         """ Fetch teams for a specific starting letter. """
#         logger.info(f"Fetching teams starting with letter '{letter.capitalize()}'...")
#         teams = {}
#         page = 1
#         while True:
#             try:
#                 url = self._format("all-teams", letter=letter, page=page)
#                 teams[page] = self.fetch_url(url)
#                 page += 1
#             except FetchError:
#                 break
#         return teams

#     def get_team_fixtures(self, team_id: str) -> dict:
#         """ Fetch fixtures for a specific team. """
#         logger.info(f"Fetching fixtures for team: {team_id} from OneFootball...")
#         url = self._format("team-fixtures", team_id=team_id)

#         data = self.fetch_url(url)

#         return {"fixtures": data}

#     def get_team_results(self, team_id: str) -> dict:
#         """ Fetch results for a specific team. """
#         logger.info(f"Fetching results for team: {team_id} from OneFootball...")
#         url = self._format("team-results", team_id=team_id)

#         data = self.fetch_url(url)

#         return {"results": data}

#     def get_team_players(self, team_id: str) -> dict:
#         """ Fetch players for a specific team. """
#         logger.info(f"Fetching players for team: {team_id} from OneFootball...")
#         url = self._format("team-players", team_id=team_id)

#         data = self.fetch_url(url)

#         return {"players": data}

#     # ---- Matches ---- #

#     def get_matches_by_date(self, date: str) -> dict:
#         """ Fetch matches for a specific date. """
#         logger.info(f"Fetching matches for date: {date} from OneFootball...")
#         self._validate_date(date)
#         url = self._format("matches", date=date)

#         data = self.fetch_url(url)

#         return {"matches": data}

#     def get_match_details(self, match_id: str) -> dict:
#         """ Fetch details for a specific match. """
#         logger.info(f"Fetching details for match: {match_id} from OneFootball...")
#         url = self._format("match-details", match_id=match_id)

#         data = self.fetch_url(url)

#         return {"match_details": data}

#     # ---- Players ---- #

#     def get_player_details(self, player_id: str) -> dict:
#         """ Fetch details for a specific player. """
#         logger.info(f"Fetching details for player: {player_id} from OneFootball...")
#         url = self._format("player-details", player_id=player_id)

#         data = self.fetch_url(url)

#         return {"player_details": data}

#     def get_player_stats(self, player_id: str, season_id: int) -> dict:
#         """ Fetch stats for a specific player. """
#         logger.info(f"Fetching stats for player: {player_id} from OneFootball...")
#         url = self._format("player-stats", player_id=player_id, season_id=season_id)

#         data = self.fetch_url(url)

#         return {"player_stats": data}

#     # ---- Helpers ---- #

#     def _format(self, endpoint_name: str, **kwargs) -> str:
#         """ Format endpoint URL with build ID, language, and other parameters. """
#         return ENDPOINTS[endpoint_name].format(build_id=self.build_id, language=self.language, **kwargs)
