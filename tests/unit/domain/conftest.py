"""Fixtures for the offline (Tier 1) domain tests."""

from typing import Any

import pytest


class OfflineProvider:
    """Stands in for a provider and fails loudly if a unit test tries to fetch anything."""

    def __getattr__(self, name: str) -> Any:
        raise AssertionError(
            f"A unit test reached the provider via '{name}'. Tier 1 tests must stay offline — "
            f"either avoid the property that fetches, or move the test to the integration suite."
        )


@pytest.fixture
def offline() -> OfflineProvider:
    return OfflineProvider()
