from abc import ABC, abstractmethod


class BaseClient(ABC):
    """
    Abstract base class for all sports clients.
    Defines a minimal common interface for generic multi-sport usage.
    """

    @abstractmethod
    def get_standings(self, *args, **kwargs):
        """ Return current standings (league, season, etc.) """
        raise NotImplementedError

    @abstractmethod
    def get_events(self, *args, **kwargs):
        """ Return matches, games, or events (past, live, upcoming, etc.) """
        raise NotImplementedError

    @abstractmethod
    def get_entities(self, *args, **kwargs):
        """ Return all teams, players, competitions or other entities """
        raise NotImplementedError

    @abstractmethod
    def get_details(self, *args, **kwargs):
        """ Return detailed information about a specific entity """
        raise NotImplementedError
