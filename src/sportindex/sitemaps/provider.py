import gzip
import logging
import re
from collections import deque
from collections.abc import Iterator
from typing import Any, TypeVar

from defusedxml import ElementTree as ET  # noqa: N817

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

class SofascoreSitemapProvider:
    """Provider class for Sofascore sitemaps fetching."""

    def __init__(self, fetcher: Fetcher = None, fetch_delay: float = 0.5):
        self._fetcher = fetcher or Fetcher()
        self._fetch_delay = fetch_delay

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

    def _extract_urls(self, root: Any) -> list[str]:
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        loc_elements = root.findall('.//sm:loc', namespaces=ns) or root.findall('.//loc')
        return [elem.text.strip() for elem in loc_elements if elem.text]

    def _traverse_sitemap_tree(self, url: str, fetch_delay: float | None = None) -> Iterator[bytes]:
        queue = deque([url])
        delay = fetch_delay if fetch_delay is not None else self._fetch_delay

        while queue:
            current_url = queue.popleft()
            logger.debug(f"Fetching sitemap URL: {current_url}")

            response = self._fetcher.fetch_url(current_url, initial_delay=delay)
            xml_bytes = gzip.decompress(response.content)

            root = ET.fromstring(xml_bytes)
            tag_name = root.tag.split('}')[-1]

            if tag_name == 'sitemapindex':
                queue.extend(self._extract_urls(root))
            elif tag_name == 'urlset':
                yield xml_bytes

    def _extract_urls_from_sitemap(self, xml_bytes: bytes) -> list[str]:
        # root = ET.fromstring(xml_bytes)
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
