import os
from collections.abc import Generator

import pytest

from sportindex import SportClient
from sportindex.api_client import SofascoreProvider
from sportindex.fetcher import RecordingFetcher
from sportindex.sitemaps import SofascoreSitemapProvider


#: Fixtures that reach the real provider — recorded or live. Any test requesting one of
#: these is an integration test, and is marked as such automatically.
PROVIDER_FIXTURES = frozenset({"client", "provider", "sitemap_provider"})


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
    fetcher = RecordingFetcher(mode="auto", cache_dir="tests/mock_cache")
    return SofascoreProvider(fetcher=fetcher, fetch_delay=0.1)

@pytest.fixture
def sitemap_provider() -> SofascoreSitemapProvider:
    return SofascoreSitemapProvider(fetch_delay=0.1, max_workers=5)
