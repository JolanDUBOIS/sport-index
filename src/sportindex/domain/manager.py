from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING

from sportindex.api_client.models import ManagerTenure as _ManagerTenure
from sportindex.api_client.models import _ManagerData
from sportindex.exceptions import (
    DomainError,
    EntityNotFoundError,
    FetchError,
    ProviderNotFoundError,
)

from .base import SearchableMixin
from .event import EventAwareMixin

if TYPE_CHECKING:
    from sportindex.api_client import SofascoreProvider

    from .collections import ScoredEntityCollection
    from .competitor import Competitor
    from .core import Country, Sport
    from .event import EventCollection

logger = logging.getLogger(__name__)


class ManagerTenure(_ManagerTenure):
    """One spell of a `Manager` at one team.

    Attributes:
        team (Competitor): The team managed during this spell.
        performance (Performance): The record over the spell — matches, wins, draws, losses,
            goals for and against, points.
        start (datetime | None): When the spell began, if the provider states it.
        end (datetime | None): When the spell ended, if the provider states it. None for an
            ongoing spell.
    """
    team: Competitor

    @classmethod
    def _from_base_schema(cls, data: _ManagerTenure, provider: SofascoreProvider) -> ManagerTenure:
        from .competitor import Competitor
        return cls(
            **data.model_dump(by_alias=True, exclude={"team"}),
            team=Competitor(data.team, provider)
        )


class Manager(SearchableMixin, EventAwareMixin):
    """Whoever runs a team from the sideline — a football manager, a Formula 1 team principal.

    Attributes:
        id (str): Globally unique SDK ID, e.g. "mng:794075".
        name (str): Full name, e.g. "Zinédine Zidane".
        slug (str): URL-friendly identifier, e.g. "zinedine-zidane".
        short_name (str): Abbreviated name, e.g. "Z. Zidane". The underlying payload field is
            optional, so this may be None despite the annotation.
        sport (Sport | None): The sport this manager works in, if the provider states it.
        country (Country | None): The manager's nationality, if the provider states it.
        team (Competitor | None): The team currently managed, if any — None between jobs.
        performances (list[ManagerTenure]): Every spell in the manager's career, each with its
            team, dates and win-loss record.
        source (_ManagerData): The parsed payload backing this entity. (inherited from BaseEntity)

    Methods:
        get_fixtures(silent: bool = False) -> EventCollection: Always empty — the provider
            offers no fixtures endpoint for managers. Logs a warning unless `silent` is True.
        get_results(silent: bool = False) -> EventCollection: The matches this manager has
            taken charge of.
        get_events() -> EventCollection: Fixtures and results combined, sorted by start time.
            In practice equal to `get_results()`, since fixtures are always empty.
            (inherited from EventAwareMixin)
        search(query: str, provider: SofascoreProvider, max_results: int = 20) -> ScoredEntityCollection[Manager]:
            Managers matching `query`, each with its relevance score, capped at `max_results`.
            (classmethod)
        from_id(entity_id: str, provider: SofascoreProvider) -> Manager: The manager with this
            SDK ID. (classmethod, inherited from IdentifiableEntity)

    Raises:
        TypeError: If constructed with data that is not `_ManagerData`.
        ValueError: If `search` is given an empty query.
        EntityNotFoundError: If `from_id` names a manager the provider does not have.
        DomainError: If the provider fails with a network or transport error.
    """
    _data: _ManagerData
    _PREFIX = "mng"
    _REPR_FIELDS = ("id", "name", "slug", "short_name", "sport", "country")

    def __init__(self, data: _ManagerData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _ManagerData):
            raise TypeError(f"Manager data must be of type _ManagerData, got {type(data)}")

        self._full_loaded = False

    @property
    def id(self) -> str:
        """The unique ID of the manager."""
        return self.encode_id(self._data.id)

    @property
    def name(self) -> str:
        """The full name of the manager."""
        return self._data.name

    @property
    def slug(self) -> str:
        """The slug of the manager (used in URLs)."""
        return self._data.slug or self._data.name.lower().replace(" ", "-")

    @property
    def short_name(self) -> str:
        """The short name of the manager, e.g. "Z. Zidane"."""
        return self._data.short_name

    @cached_property
    def sport(self) -> Sport | None:
        """The sport this manager is associated with, if any."""
        self._full_load()
        from .core import Sport
        return Sport(self._data.sport, self._provider) if self._data.sport else None

    @cached_property
    def country(self) -> Country | None:
        """The country this manager is associated with, if any."""
        from .core import Country
        return Country(self._data.country, self._provider) if self._data.country else None

    @cached_property
    def team(self) -> Competitor | None:
        """The team this manager currently manages, if any."""
        self._full_load()
        from .competitor import Competitor
        return Competitor(self._data.team, self._provider) if self._data.team else None

    @cached_property
    def performances(self) -> list[ManagerTenure]:
        """Every spell in this manager's career, each with its team, dates and record."""
        parsed_career_history = self._provider.get_manager_career_history(self._data.id)
        return [ManagerTenure._from_base_schema(parsed, provider=self._provider) for parsed in parsed_career_history]

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Fetch all fixtures for this manager."""
        from .event import EventCollection
        if not silent:
            logger.warning("No fixtures endpoint available for managers, returning empty list")
        return EventCollection()

    def get_results(self, silent: bool = False) -> EventCollection:
        """Fetch all results for this manager."""
        return self._fetch_paginated_events(self._provider.get_manager_results, self._data.id)

    @staticmethod
    def _fetch_entity(raw_id: int, provider: SofascoreProvider, **kwargs) -> _ManagerData:
        """Fetch the manager data from the provider by its raw ID."""
        try:
            return provider.get_manager(raw_id)
        except ProviderNotFoundError as e:
            logger.debug(f"Manager with id {raw_id} not found: {e}")
            raise EntityNotFoundError(f"Manager with id {raw_id} not found") from e
        except FetchError as e:
            logger.error(f"Network error while fetching manager with id {raw_id}: {e}")
            raise DomainError(f"Network error while fetching manager with id {raw_id}") from e

    @classmethod
    def search(cls, query: str, provider: SofascoreProvider, max_results: int = 20) -> ScoredEntityCollection[Manager]:
        """Search for managers matching the given query, returning up to max_results results."""
        cls._validate_query(query)
        return cls._paginate_search(
            query=query,
            provider=provider,
            search_func=provider.search_managers,
            max_results=max_results
        )
