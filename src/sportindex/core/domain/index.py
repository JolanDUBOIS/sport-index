"""
Top-level entry point for the domain layer.

The :class:`Index` is the root of the object graph.  Instantiate it
once and use it to navigate sports, categories, competitions, etc.

Example::

    from sportindex.core.domain import Index

    idx = Index()
    football = idx.sport("football")
    categories = football.categories
"""

from __future__ import annotations

from .base import BaseEntity
from .core import Sport
from ..provider.main import SofascoreProvider


class Index:
    """Root entry point — configures the provider and exposes all sports."""

    def __init__(self) -> None:
        provider = SofascoreProvider()
        BaseEntity.configure(provider)

    # -- Access -------------------------------------------------------- #

    @property
    def sports(self) -> list[Sport]:
        """All known sports (pre-defined static list)."""
        from .static import get_sports
        return list(get_sports())

    def sport(self, slug: str) -> Sport:
        """Look up a sport by slug (e.g. ``"football"``, ``"tennis"``)."""
        from .static import get_sports
        for s in get_sports():
            if s.slug == slug:
                return s
        raise KeyError(f"Unknown sport slug: {slug!r}")
