# ENDPOINTS

# # Scraping (__NEXT_DATA__)
# # ------------------------------------------------------------------
# "competition-details": f"{BASE_URL}/{{sport}}/tournament/{{category_slug}}/{{competition_slug}}/{{competition_id}}",
# "team-details": f"{BASE_URL}/{{sport}}/team/{{team_slug}}/{{team_id}}",
# "player-details": f"{BASE_URL}/{{sport}}/player/{{player_slug}}/{{player_id}}",
# "manager-details": f"{BASE_URL}/manager/{{manager_slug}}/{{manager_id}}",
# "venue-details": f"{BASE_URL}/venue/{{country_slug}}/{{venue_slug}}/{{venue_id}}",
# "event-details": f"{BASE_URL}/{{sport}}/match/{{event_slug}}/{{event_custom_id}}",


# PROVIDER METHODS

# # ---- Detailed (__NEXT_DATA__ scraping) ---- #

# def get_competition_details(self, category_slug: str, competition_slug: str, competition_id: str) -> dict:
#     """ Fetch competition details by scraping the competition page. """
#     logger.info(f"Fetching details for competition ID: {competition_id} from Sofascore...")
#     url = self._format("competition-details", category_slug=category_slug, competition_slug=competition_slug, competition_id=competition_id)
#     response = self.fetch_url(url, raw=True)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     script = soup.find('script', id="__NEXT_DATA__")
#     if not script:
#         logger.error("Failed to find __NEXT_DATA__ script tag on Sofascore competition page.")
#         raise FetchError("Could not find competition details on Sofascore page.")
#     return json.loads(script.string)

# def get_team_details(self, team_slug: str, team_id: str) -> dict:
#     """ Fetch team details by scraping the team page. """
#     logger.info(f"Fetching details for team ID: {team_id} from Sofascore...")
#     url = self._format("team-details", team_slug=team_slug, team_id=team_id)
#     response = self.fetch_url(url, raw=True)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     script = soup.find('script', id="__NEXT_DATA__")
#     if not script:
#         logger.error("Failed to find __NEXT_DATA__ script tag on Sofascore team page.")
#         raise FetchError("Could not find team details on Sofascore page.")

# def get_player_details(self, player_slug: str, player_id: str) -> dict:
#     """ Fetch player details by scraping the player page. """
#     logger.info(f"Fetching details for player ID: {player_id} from Sofascore...")
#     url = self._format("player-details", player_slug=player_slug, player_id=player_id)
#     response = self.fetch_url(url, raw=True)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     script = soup.find('script', id="__NEXT_DATA__")
#     if not script:
#         logger.error("Failed to find __NEXT_DATA__ script tag on Sofascore player page.")
#         raise FetchError("Could not find player details on Sofascore page.")
#     return json.loads(script.string)

# def get_manager_details(self, manager_slug: str, manager_id: str) -> dict:
#     """ Fetch manager details by scraping the manager page. """
#     logger.info(f"Fetching details for manager ID: {manager_id} from Sofascore...")
#     url = self._format("manager-details", manager_slug=manager_slug, manager_id=manager_id)
#     response = self.fetch_url(url, raw=True)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     script = soup.find('script', id="__NEXT_DATA__")
#     if not script:
#         logger.error("Failed to find __NEXT_DATA__ script tag on Sofascore manager page.")
#         raise FetchError("Could not find manager details on Sofascore page.")
#     return json.loads(script.string)

# def get_venue_details(self, country_slug: str, venue_slug: str, venue_id: str) -> dict:
#     """ Fetch venue details by scraping the venue page. """
#     logger.info(f"Fetching details for venue ID: {venue_id} from Sofascore...")
#     url = self._format("venue-details", country_slug=country_slug, venue_slug=venue_slug, venue_id=venue_id)
#     response = self.fetch_url(url, raw=True)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     script = soup.find('script', id="__NEXT_DATA__")
#     if not script:
#         logger.error("Failed to find __NEXT_DATA__ script tag on Sofascore venue page.")
#         raise FetchError("Could not find venue details on Sofascore page.")
#     return json.loads(script.string)

# def get_event_details(self, event_slug: str, event_custom_id: str) -> dict:
#     """ Fetch event details by scraping the event page. """
#     logger.info(f"Fetching details for event custom ID: {event_custom_id} from Sofascore...")
#     url = self._format("event-details", event_slug=event_slug, event_custom_id=event_custom_id)
#     response = self.fetch_url(url, raw=True)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     script = soup.find('script', id="__NEXT_DATA__")
#     if not script:
#         logger.error("Failed to find __NEXT_DATA__ script tag on Sofascore event page.")
#         raise FetchError("Could not find event details on Sofascore page.")
#     return json.loads(script.string)