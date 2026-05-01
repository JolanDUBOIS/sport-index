import os
from collections.abc import Generator

import pytest

from sportindex import SportClient
from sportindex.api_client import SofascoreProvider
from sportindex.fetcher import RecordingFetcher
from sportindex.sitemaps import SofascoreSitemapProvider


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
    return SofascoreSitemapProvider(fetch_delay=0.1) # No recording for sitemaps, not sure it would work...
