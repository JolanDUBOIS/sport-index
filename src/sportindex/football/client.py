import re

from . import logger
from .provider import OneFootballProvider
from ..utils import get_nested


class FootballClient:
    """ Client for accessing football data. """

    def __init__(self, provider: OneFootballProvider = None, **kwargs):
        self.provider = provider or OneFootballProvider(**kwargs)

    def get_competitions(self) -> dict:
        """ Get all competitions. """
        raw = self.provider.get_all_competitions()

        competitions = []

        for comps in raw["competitions"].values():
            containers = get_nested(comps, "pageProps.containers", [])
            for container in containers:
                content_list = get_nested(container, "type.fullWidth.component.contentType.directoryExpandedList", {})
                logger.debug(f"Content list keys: {list(content_list.keys())}")
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
            logger.debug(f"Content type keys: {list(content_type.keys())}")

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

        for teams_data in raw["teams"].values():
            containers = get_nested(teams_data, "pageProps.containers", [])
            for container in containers:
                content_list = get_nested(container, "type.fullWidth.component.contentType.directoryExpandedList", {})
                logger.debug(f"Content list keys: {list(content_list.keys())}")
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
            logger.debug(f"Content type keys: {list(content_type.keys())}")

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
                    logger.debug(f"Parsed player: {players[-1]}")

        return {"entity": entity, "players": players}

    def get_matches(self, date: str) -> dict:
        """ Get matches for a specific date. """
        raw = self.provider.get_matches_by_date(date)

        matches = []

        containers = get_nested(raw, "matches.pageProps.containers", [])
        for container in containers:
            content_type = get_nested(container, "type.fullWidth.component.contentType", {})
            logger.debug(f"Content type keys: {list(content_type.keys())}")

            if matches_container := content_type.get("matchCardsList"):
                match_cards = matches_container.get("matchCards", [])
                extras = {
                    "title": get_nested(matches_container, "sectionHeader.title"),
                    "subtitle": get_nested(matches_container, "sectionHeader.subtitle"),
                    "competition": {
                        "name": get_nested(matches_container, "sectionHeader.entityLink.name"),
                        "id": get_nested(matches_container, "sectionHeader.entityLink.urlPath", "").rsplit("/", 1)[-1] if get_nested(matches_container, "sectionHeader.entityLink.urlPath") else None,
                        "img_path": get_nested(matches_container, "sectionHeader.entityLogo.path"),
                    }
                }
                for raw_match in match_cards:
                    match = self._parse_match(raw_match)
                    match["extras"] = extras
                    matches.append(match)
        
        return {"date": date, "matches": matches}

    def get_match_details(self, match_id: str) -> dict:
        """ Get details for a specific match. """
        raw = self.provider.get_match_details(match_id)

        match = {"extras": {}}

        containers = get_nested(raw, "match_details.pageProps.containers", [])
        for container in containers:
            content_type = get_nested(container, "type.fullWidth.component.contentType", {})
            logger.debug(f"Content type keys: {list(content_type.keys())}")
            if match_details := content_type.get("matchScore"):
                match.update({
                    "id": match_id,
                    "datetime": get_nested(match_details, "kickoff.utcTimestamp"),
                    "time_period": match_details.get("timePeriod"),
                    "home_team": {
                        "id": get_nested(match_details, "homeTeam.link").rsplit("/", 1)[-1] if get_nested(match_details, "homeTeam.link") else None,
                        "name": get_nested(match_details, "homeTeam.name"),
                        "img_path": get_nested(match_details, "homeTeam.imageObject.path"),
                        "score": get_nested(match_details, "homeTeam.score"),
                        "aggregated_score": get_nested(match_details, "homeTeam.aggregatedScore"),
                        "penalties": get_nested(match_details, "homeTeam.penalties"),
                    },
                    "away_team": {
                        "id": get_nested(match_details, "awayTeam.link").rsplit("/", 1)[-1] if get_nested(match_details, "awayTeam.link") else None,
                        "name": get_nested(match_details, "awayTeam.name"),
                        "img_path": get_nested(match_details, "awayTeam.imageObject.path"),
                        "score": get_nested(match_details, "awayTeam.score"),
                        "aggregated_score": get_nested(match_details, "awayTeam.aggregatedScore"),
                        "penalties": get_nested(match_details, "awayTeam.penalties"),
                    },
                    "competition": {
                        "id": get_nested(match_details, "competition.link.urlPath").rsplit("/", 1)[-1] if get_nested(match_details, "competition.link.urlPath") else None,
                        "name": get_nested(match_details, "competition.name"),
                        "img_path": get_nested(match_details, "competition.icon.path"),
                    }
                })
            
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
                match["extras"]["events"] = events
            
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
                                match["extras"]["stadium"] = {
                                    "name": entry.get("subtitle"),
                                    "img_path": get_nested(entry, "icon.path")
                                }
                            elif entry_title == "TV guide":
                                match["extras"].setdefault("tv_guide", []).append({
                                    "name": entry.get("subtitle"),
                                    "img_path": get_nested(entry, "icon.path")
                                })

        return match

    def get_player_details(self, player_id: str) -> dict:
        """ Get details for a specific player. """
        raw = self.provider.get_player_details(player_id)

        player = {"id": player_id, "extras": {}}

        containers = get_nested(raw, "player_details.pageProps.containers", [])
        for container in containers:
            content_type = get_nested(container, "type.fullWidth.component.contentType", {})
            logger.debug(f"Content type keys: {list(content_type.keys())}")

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

    def _parse_matches(self, raw: dict, entity_id: str) -> dict:
        """ Parse matches (fixtures or results). """
        matches = []
        entity = {"id": entity_id}
        
        containers = get_nested(raw, "pageProps.containers", [])
        for container in containers:
            content_type = get_nested(container, "type.fullWidth.component.contentType", {})
            logger.debug(f"Content type keys: {list(content_type.keys())}")

            if entity_title := content_type.get("entityTitle"):
                entity.update({
                    "name": entity_title.get("title"),
                    "img_path": entity_title.get("imageObject", {}).get("path")
                })
            if fixtures_container := content_type.get("matchCardsListsAppender"):
                match_cards_list = fixtures_container.get("lists", [])
                for match_card in match_cards_list:
                    matches_list = match_card.get("matchCards", [])
                    extras = {
                        "title": get_nested(match_card, "sectionHeader.title"),
                        "subtitle": get_nested(match_card, "sectionHeader.subtitle")
                    }
                    for raw_match in matches_list:
                        match = self._parse_match(raw_match)
                        match["extras"] = extras
                        matches.append(match)
        
        return {"entity": entity, "matches": matches}

    @staticmethod
    def _parse_match(match: dict) -> dict:
        """ Parse a single match entry. """
        match_id = match.get("link").rsplit("/", 1)[-1] if match.get("link") else None
        return {
            "id": match_id,
            "datetime": match.get("kickoff"),
            "time_period": match.get("timePeriod"),
            "home_team": {
                "name": get_nested(match, "homeTeam.name"),
                "img_path": get_nested(match, "homeTeam.imageObject.path"),
                "score": get_nested(match, "homeTeam.score"),
                "aggregated_score": get_nested(match, "homeTeam.aggregatedScore"),
            },
            "away_team": {
                "name": get_nested(match, "awayTeam.name"),
                "img_path": get_nested(match, "awayTeam.imageObject.path"),
                "score": get_nested(match, "awayTeam.score"),
                "aggregated_score": get_nested(match, "awayTeam.aggregatedScore"),
            },
            "competition": {
                "name": match.get("competitionName")
            }
        }
