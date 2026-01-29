from typing import Protocol


class SportClient(Protocol):
    """
    Abstract interface for all sport clients.

    Defines the minimal common interface for multi-sport usage.
    Concrete clients (FootballClient, F1Client, etc.) must implement all methods.

    Attributes
    ----------
    sport : str
        The sport this client represents (e.g., 'football', 'f1').

    Methods
    -------
    get_standings(*args, **kwargs)
        Return current standings (league tables, season rankings, etc.)

    get_events(*args, **kwargs)
        Return matches, games, or events (past, live, upcoming, etc.)

    get_entities(*args, **kwargs)
        Return all teams, players, competitions, or other entities

    get_details(*args, **kwargs)
        Return detailed information about a specific entity
    """

    sport: str

    def get_standings(self, *args, **kwargs):
        """ Return current standings (league, season, etc.) """
        ...

    def get_events(self, *args, **kwargs):
        """ Return matches, games, or events (past, live, upcoming, etc.) """
        ...

    def get_entities(self, *args, **kwargs):
        """ Return all teams, players, competitions or other entities """
        ...

    def get_details(self, *args, **kwargs):
        """ Return detailed information about a specific entity """
        ...
