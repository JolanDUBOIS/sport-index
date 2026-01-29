from abc import ABC

from bs4 import BeautifulSoup

from .fetcher import Fetcher


class BaseScraper(ABC):
    """ TODO """
    def __init__(self, fetcher: Fetcher, **kwargs):
        self.fetcher = fetcher

    def scrape_url(self, url: str, max_retries: int = 3, retry_delay: int = 5, initial_delay: int = 5) -> BeautifulSoup:
        """ TODO """
        response = self.fetcher.fetch_url(url, max_retries, retry_delay, initial_delay)
        return BeautifulSoup(response.text, "html.parser")
