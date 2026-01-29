from .core import SportClient
from .football.client import FootballClient
from .f1.client import F1Client


class Client:
    """ Factory for creating sport-specific clients. """

    _SPORT_CLIENTS = {
        "football": FootballClient,
        "f1": F1Client,
    }

    def __new__(cls, sport: str, **kwargs) -> SportClient:
        sport = sport.lower()
        if sport not in cls._SPORT_CLIENTS:
            raise ValueError(f"Unsupported sport '{sport}'. Supported: {list(cls._SPORT_CLIENTS.keys())}")
        return cls._SPORT_CLIENTS[sport](**kwargs)
