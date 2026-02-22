"""
Base class for all domain entities.

Provides:
  - A shared provider reference (class-level, set once via configure())
  - Lazy-loading pattern (_load_full)
  - Common repr / logging
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import ClassVar, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from ..provider.main import SofascoreProvider

logger = logging.getLogger(__name__)


def _normalize_dt(value: date | datetime | None) -> datetime | None:
    """Promote a date to a datetime (midnight) for uniform comparison."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime(value.year, value.month, value.day)


class BaseEntity:
    """Root of the domain hierarchy.

    Call ``BaseEntity.configure(provider)`` once at startup.  Every
    domain object created afterwards automatically shares that provider,
    so the entire object graph uses one HTTP session.

    Sub-classes override `_load_full()` to fetch detailed data lazily.
    """

    _provider: ClassVar[SofascoreProvider]

    @classmethod
    def configure(cls, provider: SofascoreProvider) -> None:
        """Set the shared provider for all domain entities.

        Must be called once before creating any entity.
        """
        cls._provider = provider

    def __init__(self) -> None:
        self._full_loaded: bool = False
        self._raw: dict = {}

    @property
    def provider(self) -> SofascoreProvider:
        try:
            return self._provider
        except AttributeError:
            raise RuntimeError("BaseEntity.configure() must be called before using any entity") from None

    def _load_full(self) -> None:
        """Override in sub-classes to fetch extended data from the API.

        Must set `self._full_loaded = True` at the end.
        """
        self._full_loaded = True

    def __repr__(self) -> str:
        name = getattr(self, "name", None) or getattr(self, "slug", None)
        cls = type(self).__name__
        if name:
            return f"<{cls}: {name}>"
        return f"<{cls}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        id_self = getattr(self, "id", None)
        id_other = getattr(other, "id", None)
        if id_self is not None and id_other is not None:
            return id_self == id_other
        return self is other

    def __hash__(self) -> int:
        id_val = getattr(self, "id", None)
        if id_val is not None:
            return hash((type(self), id_val))
        return id(self)

    # -- Shared paginated event fetcher -------------------------------- #

    def _fetch_event_pages(
        self,
        fetch_page: Callable[[int], dict],
        *,
        max_events: int | None = None,
        before: datetime | None = None,
        after: datetime | None = None,
        ascending: bool = True,
        first_page: int = 0,
    ) -> list:
        """Paginate through a ``RawEventsResponse`` endpoint with date filtering.

        Args:
            fetch_page: ``f(page) -> RawEventsResponse`` dict.
            max_events: Collect at most this many events.
            before: Only events with ``start < before``.
            after:  Only events with ``start > after``.
            ascending: Sort direction the endpoint returns.
                       ``True`` = oldest-first (fixtures),
                       ``False`` = newest-first (results).
                       Used for early-stop optimisation.
            first_page: Page number to start from (0 or 1 depending on endpoint).

        Returns:
            A list of :class:`Event` objects.
        """
        from .event import Event

        collected: list[Event] = []
        page = first_page

        while True:
            response = fetch_page(page)
            raw_events = response.get("events", [])

            if not raw_events:
                break

            exhausted = False
            for raw in raw_events:
                ev = Event._from_raw_event(raw)
                start = ev.start

                if start is not None:
                    if before is not None and start >= before:
                        if ascending:
                            exhausted = True
                            break
                        continue
                    if after is not None and start <= after:
                        if not ascending:
                            exhausted = True
                            break
                        continue

                collected.append(ev)

                if max_events is not None and len(collected) >= max_events:
                    exhausted = True
                    break

            if exhausted or not response.get("hasNextPage", False):
                break

            page += 1

        return collected
