from . import logger
from .provider import F1Provider
from ..utils import get_nested


class F1Client:
    """ Client for accessing F1 data. """

    def __init__(self, provider: F1Provider = None):
        self.provider = provider or F1Provider()

    def get_standings(self, season: int) -> dict:
        """ Get F1 standings for a specific season. """
        raw = self.provider.get_standings(season)
        standings = {}

        standings_list = raw.get("children", [])
        for raw_standing in standings_list:
            sd_abbrev = raw_standing.get("abbreviation")
            if sd_abbrev.lower() == "driver":
                standings["drivers"] = []
                for entry in get_nested(raw_standing, "standings.entries", []):
                    standings["drivers"].append({
                        "driver": {
                            "id": get_nested(entry, "athlete.id"),
                            "name": get_nested(entry, "athlete.name"),
                            "display_name": get_nested(entry, "athlete.displayName"),
                            "short_name": get_nested(entry, "athlete.shortName"),
                            "abbreviation": get_nested(entry, "athlete.abbreviation"),
                        },
                        "extras": {"race_results": []}
                    })
                    for stat in entry.get("stats", []):
                        if stat.get("name") == "rank":
                            standings["drivers"][-1]["position"] = stat.get("value")
                        elif stat.get("name") == "championshipPts":
                            standings["drivers"][-1]["points"] = stat.get("value")
                        elif stat.get("name") == "overall":
                            pass
                        else:
                            standings["drivers"][-1]["extras"]["race_results"].append({
                                "id": stat.get("id"),
                                "name": stat.get("name"),
                                "display_name": stat.get("displayName"),
                                "short_display_name": stat.get("shortDisplayName"),
                                "points": stat.get("value")
                            })

            elif sd_abbrev.lower() == "constructor":
                standings["constructors"] = []
                for entry in get_nested(raw_standing, "standings.entries", []):
                    standings["constructors"].append({
                        "constructor": {
                            "id": get_nested(entry, "team.id"),
                            "name": get_nested(entry, "team.name"),
                            "display_name": get_nested(entry, "team.displayName"),
                            "short_name": get_nested(entry, "team.shortName"),
                            "abbreviation": get_nested(entry, "team.abbreviation"),
                            "color": get_nested(entry, "team.color"),
                        },
                        "extras": {"race_results": []}
                    })
                    for stat in entry.get("stats", []):
                        if stat.get("name") == "rank":
                            standings["constructors"][-1]["position"] = stat.get("value")
                        elif stat.get("name") == "points":
                            standings["constructors"][-1]["points"] = stat.get("value")
                        elif stat.get("name") == "overall":
                            pass
                        else:
                            standings["constructors"][-1]["extras"]["race_results"].append({
                                "id": stat.get("id"),
                                "name": stat.get("name"),
                                "display_name": stat.get("displayName"),
                                "short_display_name": stat.get("shortDisplayName"),
                                "points": stat.get("value")
                            })

        return standings

    def get_scoreboard(self, start_date: str, end_date: str) -> dict:
        """ Get F1 scoreboard for a date range. """
        raw = self.provider.get_scoreboard(start_date, end_date)
        events = []

        events_list = raw.get("events", [])
        for raw_event in events_list:
            event = {
                "id": raw_event.get("id"),
                "name": raw_event.get("name"),
                "short_name": raw_event.get("shortName"),
                "start_datetime": raw_event.get("date"),
                "end_datetime": raw_event.get("endDate"),
                "season": get_nested(raw_event, "season.year"),
                "circuit": {
                    "id": get_nested(raw_event, "circuit.id"),
                    "name": get_nested(raw_event, "circuit.fullName"),
                    "city": get_nested(raw_event, "circuit.address.city"),
                    "country": get_nested(raw_event, "circuit.address.country"),
                },
                "sessions": []
            }

            for comp in raw_event.get("competitions", []):
                event["sessions"].append({
                    "id": comp.get("id"),
                    "name": get_nested(comp, "type.abbreviation"),
                    "datetime": comp.get("date")
                })
        
            events.append(event)
        
        return {"events": events}
