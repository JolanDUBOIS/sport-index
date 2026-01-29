from abc import ABC
from datetime import date

from .fetcher import Fetcher


class BaseProvider(ABC):
    """ TODO """
    def __init__(self, fetcher: Fetcher = None, fetch_delay: float = 1, **kwargs):
        self.fetcher = fetcher or Fetcher()
        self.fetch_delay = fetch_delay

    def fetch_url(self, url: str) -> dict:
        response = self.fetcher.fetch_url(url, initial_delay=self.fetch_delay)
        return response.json()

    @staticmethod
    def _validate_date(date_str: str) -> None:
        try:
            date.fromisoformat(date_str)
        except ValueError:
            raise ValueError("date must be in YYYY-MM-DD format")