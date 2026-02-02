from sportindex import Client, F1Client


if __name__ == "__main__":
    # Initialize client
    client: F1Client = Client("f1", provider="espn")

    # Get events for the 2025 season
    events = client.get_events(start_date="2025-01-01", end_date="2025-12-31")
    print(events)
