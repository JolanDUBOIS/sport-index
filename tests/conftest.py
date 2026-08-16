import gzip
import os
from collections.abc import Generator
from pathlib import Path

import pytest
from curl_cffi.requests.models import Response

from sportindex import SportClient
from sportindex.api_client import SofascoreProvider
from sportindex.fetcher import Fetcher, RecordingFetcher
from sportindex.sitemaps import SofascoreSitemapProvider


#: Fixtures that reach the real provider — recorded or live. Any test requesting one of
#: these is an integration test, and is marked as such automatically. `sitemap_provider`
#: is absent on purpose: it is served entirely from local files.
PROVIDER_FIXTURES = frozenset({"client", "provider"})

SITEMAP_FIXTURES_DIR = Path(__file__).parent / "fixtures" / "sitemaps"


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Mark every test that touches the provider as `integration`.

    Done by fixture usage rather than by file path so a new test is classified correctly
    wherever it is written, without anyone having to remember the marker.
    """
    for item in items:
        if PROVIDER_FIXTURES & set(getattr(item, "fixturenames", ())):
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment()-> Generator[None, None, None]:
    """Automatically set environment variables for all tests."""
    os.environ["SPORTINDEX_RECORD_MODE"] = os.environ.get("SPORTINDEX_RECORD_MODE") or "auto"
    os.environ["SPORTINDEX_FIXTURES_DIR"] = "tests/mock_cache"

    yield

    os.environ.pop("SPORTINDEX_RECORD_MODE", None)
    os.environ.pop("SPORTINDEX_FIXTURES_DIR", None)

@pytest.fixture
def client() -> SportClient:
    return SportClient()

@pytest.fixture
def provider() -> SofascoreProvider:
    # Read from the environment rather than hardcoding "auto", so that `replay` really
    # does keep the whole suite off the network — a hardcoded mode would quietly fetch.
    fetcher = RecordingFetcher(
        mode=os.environ["SPORTINDEX_RECORD_MODE"],
        cache_dir=os.environ["SPORTINDEX_FIXTURES_DIR"],
    )
    return SofascoreProvider(fetcher=fetcher, fetch_delay=0.1)

class StaticSitemapFetcher(Fetcher):
    """Serves sitemaps from `tests/fixtures/sitemaps`, never from the network.

    Unlike the API, the sitemap tree is a fixed, well-known shape, so there is nothing worth
    recording — the fixtures are hand-written miniatures of the real files. They are stored
    as plain XML so they stay readable and diffable, and gzipped here because that is how
    the provider serves them.
    """

    def __init__(self, fixtures_dir: Path = SITEMAP_FIXTURES_DIR) -> None:
        super().__init__()
        self.fixtures_dir = fixtures_dir

    def fetch_url(self, url: str, **kwargs) -> Response:
        path = self.fixtures_dir / url.rsplit("/", 1)[-1].removesuffix(".gz")
        if not path.exists():
            raise FileNotFoundError(f"No sitemap fixture for {url} (expected {path})")

        response = Response()
        response.status_code = 200
        response.content = gzip.compress(path.read_bytes())
        response.url = url
        return response


@pytest.fixture
def sitemap_provider() -> SofascoreSitemapProvider:
    return SofascoreSitemapProvider(fetcher=StaticSitemapFetcher(), fetch_delay=0, max_workers=5)
