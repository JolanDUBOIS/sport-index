import logging
from importlib.metadata import version, PackageNotFoundError

logging.getLogger(__name__).addHandler(logging.NullHandler())

try:
    __version__ = version("sport-index")
except PackageNotFoundError:
    __version__ = "unknown"

from .client import Client
from .core import SportClient

__all__ = ["__version__", "Client", "SportClient"]