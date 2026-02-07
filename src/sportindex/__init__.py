"""
sport-index: Unified Python clients for sports data.

Provides a factory (`Client`) to create sport-specific clients, an interface
(`SportClient`) for typing, and concrete clients (`FootballClient`, `F1Client`).

Note: This library accesses unofficial APIs and may rely on scraping.
Use responsibly and comply with provider terms of service.
"""

import logging
from importlib.metadata import version, PackageNotFoundError

logging.getLogger(__name__).addHandler(logging.NullHandler())

try:
    __version__ = version("sport-index")
except PackageNotFoundError:
    __version__ = "unknown"

# from .client_old import Client
# from .core import SportClient
# from .f1 import F1Client
# from .football import FootballClient

__all__ = [
    # "__version__",
    # "SportClient",
    # "Client",
    # "FootballClient",
    # "F1Client",
]