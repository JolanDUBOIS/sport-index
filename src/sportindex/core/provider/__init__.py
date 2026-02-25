"""
provider — Lightweight Sofascore provider returning raw typed dicts.

Usage:
    from sportindex.core.provider import SofascoreProvider
    from sportindex.core.transformers import parse_periods, get_event_outcome

    provider = SofascoreProvider()
    event = provider.get_event("12345678")

    # Access raw fields directly (IDE autocomplete works via TypedDicts)
    print(event["homeTeam"]["name"])

    # Use transformers for complex derived data
    periods = parse_periods(event)
    outcome = get_event_outcome(event)
"""
import logging
logger = logging.getLogger(__name__)

from .main import SofascoreProvider

__all__ = ["SofascoreProvider"]
