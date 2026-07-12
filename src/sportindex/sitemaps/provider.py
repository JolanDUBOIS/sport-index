import gzip
import logging
import re
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, TypeVar

from ..fetcher import Fetcher
from .endpoints import ENDPOINTS
from .models import (
    _ManagerStub,
    _PlayerStub,
    _RaceStub,
    _SitemapStub,
    _TeamStub,
    _TournamentStub,
    _VenueStub,
)

logger = logging.getLogger(__name__)


T = TypeVar('T', bound=_SitemapStub)

LOC_REGEX = re.compile(b"<[^>]*loc>([^<]+)</[^>]*loc>")
SITEMAPINDEX_TAG = b"sitemapindex"
URLSET_TAG = b"urlset"

class SofascoreSitemapProvider:
    """Provider class for Sofascore sitemaps fetching."""

    def __init__(self, fetcher: Fetcher | None = None, fetch_delay: float = 0.5, max_workers: int = 10):
        self._fetcher = fetcher or Fetcher()
        self._fetch_delay = fetch_delay
        self._max_workers = max_workers

    def get_managers_list(self) -> list[_ManagerStub]:
        url = self._format("managers")
        return self._fetch_and_parse_sitemap(url, _ManagerStub)

    def get_players_list(self, sport_slug: str | None = None) -> list[_PlayerStub]:
        sport_slug = sport_slug or "index"
        # Will fetch the node sitemap with all players from all sports
        url = self._format("players", sport_slug=sport_slug)
        return self._fetch_and_parse_sitemap(url, _PlayerStub)

    def get_races_list(self) -> list[_RaceStub]:
        url = self._format("races")
        return self._fetch_and_parse_sitemap(url, _RaceStub)

    def get_teams_list(self, sport_slug: str | None = None) -> list[_TeamStub]:
        sport_slug = sport_slug or "index"
        url = self._format("teams", sport_slug=sport_slug)
        return self._fetch_and_parse_sitemap(url, _TeamStub)

    def get_tournaments_list(self, sport_slug: str | None = None) -> list[_TournamentStub]:
        sport_slug = sport_slug or "index"
        url = self._format("tournaments", sport_slug=sport_slug)
        return self._fetch_and_parse_sitemap(url, _TournamentStub)

    def get_venues_list(self) -> list[_VenueStub]:
        url = self._format("venues")
        return self._fetch_and_parse_sitemap(url, _VenueStub)

    def _format(self, endpoint_name: str, **kwargs: Any) -> str:
        """Format an endpoint URL from the endpoint registry."""
        if endpoint_name not in ENDPOINTS:
            raise ValueError(f"Endpoint '{endpoint_name}' is not defined.")
        return ENDPOINTS[endpoint_name].format(**kwargs)

    def _fetch_and_decompress(self, url: str) -> tuple[str, bytes]:
        response = self._fetcher.fetch_url(url, initial_delay=self._fetch_delay)
        return url, gzip.decompress(response.content)

    def _traverse_sitemap_tree(self, initial_url: str) -> Iterator[bytes]:
        queue = [initial_url]

        while queue:
            current_batch = queue[:]
            queue.clear()

            with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
                futures = {executor.submit(self._fetch_and_decompress, url): url for url in current_batch}

                for future in as_completed(futures):
                    try:
                        _, xml_bytes = future.result()
                        head = xml_bytes[:256].lower()

                        if SITEMAPINDEX_TAG in head:
                            queue.extend(match.decode('utf-8').strip() for match in LOC_REGEX.findall(xml_bytes))
                        elif URLSET_TAG in head:
                            yield xml_bytes
                    except Exception as e:
                        logger.exception(f"Error fetching/parsing sitemap URL: {e}")

    def _extract_urls_from_sitemap(self, xml_bytes: bytes) -> list[str]:
        return [match.decode('utf-8').strip() for match in LOC_REGEX.findall(xml_bytes)]

    def _fetch_and_parse_sitemap(self, url: str, model_cls: type[T]) -> list[T]:
        stubs = []
        for xml_bytes in self._traverse_sitemap_tree(url):
            stub_urls = self._extract_urls_from_sitemap(xml_bytes)
            try:
                batch_stubs = model_cls.from_url_batch(stub_urls)
                stubs.extend(batch_stubs)
            except Exception as e:
                logger.exception(f"Error parsing batch of URLs: {e}")
        return stubs
