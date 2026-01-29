from datetime import date

from .endpoints import ENDPOINTS
from sportindex.core import BaseProvider


class ESPNProvider(BaseProvider):
    """ TODO """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_standings(self, season: int) -> dict:
        """ Fetch F1 standings. """
        url = ENDPOINTS["standings"].format(season=season)
        return self.fetch_url(url)

    def get_scoreboard(self, start_date: str, end_date: str) -> dict:
        """ Fetch F1 scoreboard for a date range. """
        dates = f"{self._to_provider_date(start_date)}-{self._to_provider_date(end_date)}"
        url = ENDPOINTS["scoreboard"].format(dates=dates)
        return self.fetch_url(url)

    @staticmethod
    def _to_provider_date(date_str: str) -> str:
        d = date.fromisoformat(date_str)
        return d.strftime("%Y%m%d")
