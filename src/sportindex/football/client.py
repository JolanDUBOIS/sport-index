"""
Football client.

See docs/football/DATA_CONTRACT.md for output structures and guarantees.
"""

import re

from .onefootball import OneFootballProvider
from sportindex.utils import get_nested
from sportindex.core import SportClient


class FootballClient(SportClient):
    """
    Client for accessing football data from supported providers.

    This client provides access to competitions, standings, matches, teams, 
    players, and detailed information for football leagues. Certain methods 
    allow filtering by date, competition, or team.

    Attributes
    ----------
    sport : str
        The sport this client represents. Always "football".
    provider : str, optional
        The data provider to use. Default is 'onefootball'. Must be one of:
        'onefootball'.
    **kwargs
        Additional keyword arguments passed to the provider's constructor.

    Methods
    -------
    get_standings(competition_id: str) -> dict
        Return standings for a specific competition.

    get_events(on: str = "date", **kwargs) -> dict
        Return matches or events based on the 'on' parameter. Supported
        values for 'on':
        - 'date' → requires 'date' keyword argument
        - 'competition' → requires 'competition_id'
        - 'team' → requires 'team_id'
        - 'team_results' → requires 'team_id'

    get_entities(entity_type: str, **kwargs) -> dict
        Return entities based on 'entity_type'. Supported values:
        - 'competitions'
        - 'teams'
        - 'players' (requires 'team_id')

    get_details(detail_type: str, entity_id: str) -> dict
        Return detailed information based on 'detail_type'. Supported values:
        - 'match'
        - 'player'

    get_competitions() -> dict
        Return all competitions available from the provider.

    get_competition_standings(competition_id: str) -> dict
        Return detailed standings for a specific competition.

    get_competition_fixtures(competition_id: str) -> dict
        Return upcoming fixtures for a specific competition.

    get_competition_results(competition_id: str) -> dict
        Return past results for a specific competition.

    get_teams() -> dict
        Return all teams available from the provider.

    get_team_fixtures(team_id: str) -> dict
        Return upcoming fixtures for a specific team.

    get_team_results(team_id: str) -> dict
        Return past results for a specific team.

    get_team_players(team_id: str) -> dict
        Return players for a specific team.

    get_matches(date: str) -> dict
        Return matches for a specific date.

    get_match_details(match_id: str) -> dict
        Return detailed information for a specific match.

    get_player_details(player_id: str) -> dict
        Return detailed information for a specific player.

    get_player_stats(player_id: str, season_id: int) -> dict
        Return player statistics for a given season. Not yet implemented.
    """

    sport: str = "football"

    _PROVIDERS = {
        "onefootball": OneFootballProvider,
    }

    def __init__(self, provider: str = None, **kwargs):
        if provider is None:
            self.provider = OneFootballProvider(**kwargs)
        else:
            provider_class = self._PROVIDERS.get(provider.lower())
            if provider_class is None:
                raise ValueError(f"Unknown Football provider: {provider}. Valid options are: {list(self._PROVIDERS.keys())}")
            self.provider = provider_class(**kwargs)

    # --- Implemented methods from SportClient --- #

    def get_standings(self, competition_id: str) -> dict:
        """ Get standings for a specific competition. """
        return self.get_competition_standings(competition_id)

    def get_events(self, on: str = "date", **kwargs) -> dict:
        """
        Get matches, games, or events based on the 'on' parameter.
        Supported 'on' values: date, competition, team, team_results.
        """
        if on == "date":
            date = kwargs.get("date")
            if not date:
                raise ValueError("Date parameter is required when 'on' is set to 'date'.")
            return self.get_matches(date)
        elif on == "competition":
            competition_id = kwargs.get("competition_id")
            if not competition_id:
                raise ValueError("competition_id parameter is required when 'on' is set to 'competition'.")
            return self.get_competition_fixtures(competition_id)
        elif on == "team":
            team_id = kwargs.get("team_id")
            if not team_id:
                raise ValueError("team_id parameter is required when 'on' is set to 'team'.")
            return self.get_team_fixtures(team_id)
        elif on == "team_results":
            team_id = kwargs.get("team_id")
            if not team_id:
                raise ValueError("team_id parameter is required when 'on' is set to 'team_results'.")
            return self.get_team_results(team_id)
        else:
            raise ValueError(f"Unsupported 'on' parameter value: {on}")

    def get_entities(self, entity_type: str, **kwargs) -> dict:
        """
        Get entities based on the 'entity_type' parameter.
        Supported 'entity_type' values: competitions, teams, players.
        """
        if entity_type == "competitions":
            return self.get_competitions()
        elif entity_type == "teams":
            return self.get_teams()
        elif entity_type == "players":
            team_id = kwargs.get("team_id")
            if not team_id:
                raise ValueError("team_id parameter is required when 'entity_type' is set to 'players'.")
            return self.get_team_players(team_id)
        else:
            raise ValueError(f"Unsupported 'entity_type' parameter value: {entity_type}")

    def get_details(self, detail_type: str, entity_id: str) -> dict:
        """
        Get details based on the 'detail_type' parameter.
        Supported 'detail_type' values: match, player.
        """
        if detail_type == "match":
            return self.get_match_details(entity_id)
        elif detail_type == "player":
            return self.get_player_details(entity_id)
        else:
            raise ValueError(f"Unsupported 'detail_type' parameter value: {detail_type}")

    # --- Competitions --- #

    def get_competitions(self) -> dict:
        """ Get all competitions. """
        raw = self.provider.get_all_competitions()

        competitions = []

        for comps in raw["competitions"].values():
            containers = get_nested(comps, "pageProps.containers", [])
            for container in containers:
                content_list = get_nested(container, "type.fullWidth.component.contentType.directoryExpandedList", {})
                if links := content_list.get("links"):
                    competitions.extend(links)
                    continue

        for competition in competitions:
            competition["id"] = competition.get("urlPath", "").rsplit("/", 1)[-1] if competition.get("urlPath", "") else None
            for key in list(competition.keys()):
                if key not in ("id", "name"):
                    competition.pop(key)

        return {"competitions": competitions}

    def get_competition_standings(self, competition_id: str) -> dict:
        """ Get standings for a specific competition. """
        raw = self.provider.get_competition_standings(competition_id)

        standings = []
        competition = {"id": competition_id}

        containers = get_nested(raw, "standings.pageProps.containers", [])
        for container in containers:
            content_type = get_nested(container, "type.fullWidth.component.contentType", {})

            if entity_title := content_type.get("entityTitle"):
                competition.update({
                    "name": entity_title.get("title"),
                    "img_path": entity_title.get("imageObject", {}).get("path")
                })

            if standings_container := content_type.get("standings"):
                rows = standings_container.get("rows", [])
                for row in rows:
                    team_id = row.get("teamPath").rsplit("/", 1)[-1] if row.get("teamPath") else None
                    standings.append({
                        "team": {
                            "id": team_id,
                            "name": row.get("teamName"),
                            "img_path": row.get("imageObject", {}).get("path")
                        },
                        "position": row.get("position"),
                        "position_change": row.get("positionChange"),
                        "played": row.get("playedMatchesCount"),
                        "won": row.get("wonMatchesCount"),
                        "drawn": row.get("drawnMatchesCount"),
                        "lost": row.get("lostMatchesCount"),
                        "goal_difference": row.get("goalsDiff"),
                        "points": row.get("points"),
                    })

        return {"competition": competition, "standings": standings}

    def get_competition_fixtures(self, competition_id: str) -> dict:
        """ Get fixtures for a specific competition. """
        raw = self.provider.get_competition_fixtures(competition_id)
        return self._parse_matches(raw.get("fixtures"), competition_id)

    def get_competition_results(self, competition_id: str) -> dict:
        """ Get results for a specific competition. """
        raw = self.provider.get_competition_results(competition_id)
        return self._parse_matches(raw.get("results"), competition_id)

    def get_teams(self) -> dict:
        """ Get all teams. """
        raw = self.provider.get_all_teams()

        teams = []

        for letter_teams in raw["teams"].values(): # Iterate over letters
            for teams_data in letter_teams.values(): # Iterate over pages
                containers = get_nested(teams_data, "pageProps.containers", [])
                for container in containers:
                    content_list = get_nested(container, "type.fullWidth.component.contentType.directoryExpandedList", {})
                    if links := content_list.get("links"):
                        teams.extend(links)
                        continue
        
        for team in teams:
            team["id"] = team.get("urlPath", "").rsplit("/", 1)[-1] if team.get("urlPath", "") else None
            for key in list(team.keys()):
                if key not in ("id", "name"):
                    team.pop(key)
        
        return {"teams": teams}

    def get_team_fixtures(self, team_id: str) -> dict:
        """ Get fixtures for a specific team. """
        raw = self.provider.get_team_fixtures(team_id)
        return self._parse_matches(raw.get("fixtures"), team_id)

    def get_team_results(self, team_id: str) -> dict:
        """ Get results for a specific team. """
        raw = self.provider.get_team_results(team_id)
        return self._parse_matches(raw.get("results"), team_id)
        
    def get_team_players(self, team_id: str) -> dict:
        """ Get players for a specific team. """
        raw = self.provider.get_team_players(team_id)

        players = []
        entity = {"id": team_id}

        containers = get_nested(raw, "players.pageProps.containers", [])
        for container in containers:
            content_type = get_nested(container, "type.fullWidth.component.contentType", {})

            if entity_title := content_type.get("entityTitle"):
                entity.update({
                    "name": entity_title.get("title"),
                    "img_path": entity_title.get("imageObject", {}).get("path")
                })

            if squad_container := content_type.get("entityNavigation"):
                partial_squad_list = squad_container.get("links", [])
                for player in partial_squad_list:
                    player_id = player.get("urlPath").rsplit("/", 1)[-1] if player.get("urlPath") else None

                    title = player.get("title")
                    title_match = re.match(r"^(.*)\s+\((\d+)\)$", title.strip())
                    player_name = title_match.group(1) if title_match else title.strip()
                    player_number = int(title_match.group(2)) if title_match else None

                    players.append({
                        "id": player_id,
                        "name": player_name,
                        "number": player_number,
                        "position": player.get("subtitle"),
                        "img_path": player.get("logo", {}).get("path")
                    })

        return {"entity": entity, "players": players}

    def get_matches(self, date: str) -> dict:
        """ Get matches for a specific date. """
        raw = self.provider.get_matches_by_date(date)

        matches = self._parse_matches(raw.get("matches", [])).get("matches", [])
        return {"date": date, "matches": matches}

    def get_match_details(self, match_id: str) -> dict:
        """ Get details for a specific match. """
        raw = self.provider.get_match_details(match_id)

        match = self._parse_match({}) # Initialize empty match structure
        containers = get_nested(raw, "match_details.pageProps.containers", [])
        for container in containers:
            content_type = get_nested(container, "type.fullWidth.component.contentType", {})
            if match_details := content_type.get("matchScore"):
                match = self._parse_match(match_details)
            
            if match_events := content_type.get("matchEvents"):
                events = []
                for event in match_events.get("events", []):
                    event_type_case = event.get("type", {}).get("$case")
                    extras = event.get("type", {}).get(event_type_case, {})
                    extras.pop("type", None)
                    events.append({
                        "name": event.get("name"),
                        "minute": event.get("timeline"),
                        "team": "home" if event.get("teamSide") == 0 else "away",
                        "extras": extras
                    })
                match["details"]["events"] = events
            
            # TODO - Lineups

            match_items = get_nested(container, "type.grid.items", [])
            for item in match_items:
                components = get_nested(item, "components", [])
                for component in components:
                    match_info = get_nested(component, "contentType.matchInfo", None)
                    if match_info:
                        entries = match_info.get("entries", [])
                        for entry in entries:
                            entry_title = entry.get("title")
                            if entry_title == "Stadium":
                                match["details"]["stadium"] = {
                                    "name": entry.get("subtitle"),
                                    "img_path": get_nested(entry, "icon.path")
                                }
                            elif entry_title == "TV guide":
                                match["details"].setdefault("tv_guide", []).append({
                                    "name": entry.get("subtitle"),
                                    "img_path": get_nested(entry, "icon.path")
                                })

        match["id"] = match_id # Match details do not include ID, so we set it here
        return match

    def get_player_details(self, player_id: str) -> dict:
        """ Get details for a specific player. """
        raw = self.provider.get_player_details(player_id)

        player = {"id": player_id, "extras": {}}

        containers = get_nested(raw, "player_details.pageProps.containers", [])
        for container in containers:
            content_type = get_nested(container, "type.fullWidth.component.contentType", {})

            if transfer_head := content_type.get("transferHeader"):
                player["name"] = get_nested(transfer_head, "transferPlayerHeader.playerName")
            
            if entity_navigation := content_type.get("entityNavigation"):
                links = entity_navigation.get("links", [])
                for team in links:
                    team_id = team.get("urlPath").rsplit("/", 1)[-1] if team.get("urlPath") else None
                    player["extras"].setdefault("teams", []).append({
                        "id": team_id,
                        "name": team.get("title"),
                        "img_path": team.get("logo", {}).get("path")
                    })

            if player_info := content_type.get("transferDetails"):
                entries = player_info.get("entries", [])
                for entry in entries:
                    entry_subtitle = entry.get("subtitle")
                    if entry_subtitle == "Position":
                        player["position"] = entry.get("title")
                    elif entry_subtitle == "Age":
                        player["age"] = entry.get("title")
                    elif entry_subtitle == "Country":
                        player["country"] = entry.get("title")
                    elif entry_subtitle == "Height":
                        player["height"] = entry.get("title")
                    elif entry_subtitle == "Weight":
                        player["weight"] = entry.get("title")
                    elif entry_subtitle == "Jersey number":
                        player["number"] = entry.get("title")

        return player

    def get_player_stats(self, player_id: str, season_id: int) -> dict:
        """ Get stats for a specific player. """
        raise NotImplementedError("Player stats parsing not yet implemented.")

    # --- Helpers --- #

    def _parse_matches(self, raw: dict, entity_id: str | None = None) -> dict:
        """ Parse matches (fixtures or results). """
        matches = []
        entity = {}
        
        containers = get_nested(raw, "pageProps.containers", [])
        for container in containers:
            content_type = get_nested(container, "type.fullWidth.component.contentType", {})

            if entity_title := content_type.get("entityTitle"):
                entity = {
                    "id": entity_id,
                    "name": entity_title.get("title"),
                    "img_path": entity_title.get("imageObject", {}).get("path")
                }
            if fixtures_container := content_type.get("matchCardsListsAppender"):
                match_cards_list = fixtures_container.get("lists", [])
                for match_card in match_cards_list:
                    matches_list = match_card.get("matchCards", [])
                    for raw_match in matches_list:
                        match = self._parse_match(raw_match)
                        match["competition"]["name"] = match.get("competitionName") or get_nested(match, "competition.name")
                        match["contextual"]["stage_label"] = get_nested(match_card, "sectionHeader.subtitle")
                        matches.append(match)
            elif fixtures_container := content_type.get("matchCardsList"):
                matches_list = fixtures_container.get("matchCards", [])
                for match_card in matches_list:
                    match = self._parse_match(match_card)
                    match["competition"] = {
                        "id": get_nested(fixtures_container, "sectionHeader.entityLink.urlPath").rsplit("/", 1)[-1] if get_nested(fixtures_container, "sectionHeader.entityLink.urlPath") else None,
                        "name": get_nested(fixtures_container, "sectionHeader.title"),
                        "img_path": get_nested(fixtures_container, "sectionHeader.entityLogo.path"),
                    }
                    match["contextual"]["stage_label"] = get_nested(fixtures_container, "sectionHeader.subtitle")
                    matches.append(match)

        return {"entity": entity, "matches": matches}

    @staticmethod
    def _parse_match(match: dict) -> dict:
        match_id = match.get("link").rsplit("/", 1)[-1] if match.get("link") else None
        return {
            "id": match_id or match.get("matchId"),
            "datetime": get_nested(match, "kickoff.utcTimestamp") or match.get("kickoff"),
            "time_period": match.get("timePeriod"),
            "home_team": {
                "id": get_nested(match, "homeTeam.link").rsplit("/", 1)[-1] if get_nested(match, "homeTeam.link") else None,
                "name": get_nested(match, "homeTeam.name"),
                "img_path": get_nested(match, "homeTeam.imageObject.path"),
                "score": get_nested(match, "homeTeam.score"),
                "aggregated_score": get_nested(match, "homeTeam.aggregatedScore"),
                "penalties": get_nested(match, "homeTeam.penalties"),
            },
            "away_team": {
                "id": get_nested(match, "awayTeam.link").rsplit("/", 1)[-1] if get_nested(match, "awayTeam.link") else None,
                "name": get_nested(match, "awayTeam.name"),
                "img_path": get_nested(match, "awayTeam.imageObject.path"),
                "score": get_nested(match, "awayTeam.score"),
                "aggregated_score": get_nested(match, "awayTeam.aggregatedScore"),
                "penalties": get_nested(match, "awayTeam.penalties"),
            },
            "competition": {
                "id": get_nested(match, "competition.link.urlPath").rsplit("/", 1)[-1] if get_nested(match, "competition.link.urlPath") else None,
                "name": None,  # Filled by list-level context when available
                "img_path": get_nested(match, "competition.icon.path"),
            },
            "contextual": {
                "stage_label": None,
            },
            "details": {},
        }
