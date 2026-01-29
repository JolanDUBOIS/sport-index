from sportindex import Client


if __name__ == "__main__":
    # Initialize client
    client = Client("football", provider="onefootball")

    # Get all matches for a specific team (e.g., Paris Saint-Germain)
    matches = client.get_team_fixtures(team_id="psg-263")
    for match in matches["matches"]:
        print(f'{match["datetime"]}: {match["home_team"]["name"]} vs {match["away_team"]["name"]}')

    # Get details for a specific match (e.g. Bayer Leverkusen vs PSG)
    match_details = client.get_match_details(match_id="2636478")
    print(f'{match_details["datetime"]}: {match_details["home_team"]["name"]} vs {match_details["away_team"]["name"]}')
    print(f'Competition: {match_details["competition"]["name"]}')
    for event in match_details.get("extras", {}).get("events", []):
        if event["name"] in ["Goal", "Penalty"]:
            team = "Bayer Leverkusen" if event["team"] == "home" else "Paris Saint-Germain"
            print(f'{event["name"]} scored by {event["extras"]["scorer"]["name"]} at {event["minute"]} minute for {team}')
