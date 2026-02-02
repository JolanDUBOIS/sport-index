import logging

logging.basicConfig(
    level=logging.DEBUG,  # or INFO
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

import json
import argparse
from pathlib import Path

from sportindex import Client


SAMPLE_COLLECTION_MAP = {
    "football": {
        # "get_competitions": {},
        "get_competition_standings": {"competition_id": "uefa-champions-league-5"},
        "get_competition_fixtures": {"competition_id": "uefa-champions-league-5"},
        "get_competition_results": {"competition_id": "uefa-champions-league-5"},
        # "get_teams": {},
        "get_team_fixtures": {"team_id": "psg-263"},
        "get_team_results": {"team_id": "psg-263"},
        "get_team_players": {"team_id": "psg-263"},
        "get_matches": {"date": "2026-01-28"},
        "get_match_details": {"match_id": "2636478"},
        "get_player_details": {"player_id": "marquinhos-33354"}
    },
    "f1": {
        "get_standings": {"season": "2025"},
        "get_events": {"start_date": "2025-01-01", "end_date": "2025-12-31"}
    }
}

def main():
    parser = argparse.ArgumentParser(description="Collect sample outputs from clients.")
    parser.add_argument("--sport", type=str, help="Sport to fetch samples for", required=True)
    args = parser.parse_args()

    sport = args.sport

    logger.info(f"Running sample collection script for sport: {sport}")

    client = Client(sport, fetch_delay=0.1)

    for method_name, params in SAMPLE_COLLECTION_MAP.get(sport, {}).items():
        method = getattr(client, method_name)
        logger.info(f"Collecting sample for method: {method_name} with params: {params}")
        sample_output = method(**params)

        output_filename = Path(__file__).parent.parent / "data" / sport / f"{method_name}_sample.json"
        output_filename.parent.mkdir(parents=True, exist_ok=True)
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(sample_output, f, ensure_ascii=False, indent=4)
        logger.info(f"Sample output saved to: {output_filename}")
