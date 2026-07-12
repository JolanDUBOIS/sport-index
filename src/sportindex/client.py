from __future__ import annotations

import logging
import os
from collections import defaultdict
from typing import Any, Literal, TypeVar, overload

from .api_client import SofascoreProvider
from .domain import (
    Category,
    Competition,
    Competitor,
    Country,
    EntityCollection,
    Event,
    IdentifiableEntity,
    SearchableMixin,
    Season,
    Sport,
)
from .exceptions import EntityNotFoundError
from .fetcher import Fetcher, RecordingFetcher

logger = logging.getLogger(__name__)


_default_provider = None

def _get_default_provider() -> SofascoreProvider:
    global _default_provider
    if _default_provider is None:
        record_mode = os.getenv("SPORTINDEX_RECORD_MODE")
        fixtures_dir = os.getenv("SPORTINDEX_FIXTURES_DIR", "tests/fixtures")

        if record_mode in ("record", "replay", "auto"):
            logger.info(f"Initialized SportClient in testing mode: '{record_mode}' (Dir: {fixtures_dir})")
            fetcher = RecordingFetcher(mode=record_mode, cache_dir=fixtures_dir)
        else:
            logger.info("Initialized SportClient in standard LIVE mode.")
            fetcher = Fetcher()

        _default_provider = SofascoreProvider(fetcher=fetcher)
    return _default_provider


S = TypeVar("S", bound="SearchableMixin")
E = TypeVar("E", bound="IdentifiableEntity")

class SportClient:
    """Main client for accessing sports data.

    Provides methods to fetch sports, countries, categories, competitions, events, competitors, managers, referees, venues, etc. in a unified, object-oriented way.
    Caches entities in memory to minimize redundant API calls and improve performance. Cache can be cleared manually if needed.

    Methods:
        get(entity_cls: type[IdentifiableEntity], entity_id: str) -> Optional[IdentifiableEntity]: Fetch an identifiable entity by its class and ID.
        search(entity_cls: type[SearchableMixin], query: str, max_results: int = 20) -> EntityCollection[SearchableMixin]: Search for entities that implement SearchableMixin.
        list(entity_cls: type[IdentifiableEntity], **kwargs) -> EntityCollection: List entities of a given class with optional filters (e.g., list competitions by category_id).

    Usage:
        >>> client = SportClient()
        >>> sport = client.get(Sport, "spt:1")
        >>> sport = client.get("spt:1")  # entity_cls is optional: resolved from the ID's prefix
        >>> events = client.list(Event, season_id="trnc:123:trns:456")
        >>> referee = client.search(Referee, query="John Doe")

    Raises:
        EntityNotFoundError: If a requested entity does not exist.
    """

    def __init__(self):
        """Initialize the SportClient.

        Initializes in-memory caches for all entity types.
        """
        self._provider = _get_default_provider()

        self._cache: dict[str, dict[str, Any]] = defaultdict(dict)

    def _resolve_ns(self, entity_cls: type[IdentifiableEntity]) -> str:
        """
        Map a class to its canonical cache namespace.
        Ensures MatchEvent/StageEvent share 'event' and Team/Athlete share 'competitor'.
        """
        if issubclass(entity_cls, Event):
            return "event"
        if issubclass(entity_cls, Competitor):
            return "competitor"
        return entity_cls.__name__.lower()

    # --- Cache Helpers ---

    def _get_cached(self, entity_cls: type[E], entity_id: str) -> E | None:
        """Return an entity from the cache if it exists.

        Args:
            entity_cls (type[IdentifiableEntity]): The class of the entity to retrieve.
            entity_id (str): The unique identifier of the entity.

        Returns:
            Optional[IdentifiableEntity]: The cached entity, or None if not found.
        """
        ns = self._resolve_ns(entity_cls)
        return self._cache[ns].get(entity_id)

    def _set_cached(self, entity_cls: type[E], entity: E) -> E:
        """Add an entity to the cache and return it.

        Args:
            entity_cls (type[IdentifiableEntity]): The class of the entity to store.
            entity (IdentifiableEntity): The entity to store.

        Returns:
            IdentifiableEntity: The same entity for chaining.
        """
        ns = self._resolve_ns(entity_cls)
        self._cache[ns][entity.id] = entity
        return entity

    def _hydrate_cache(self, entity_cls: type[E], collection: EntityCollection) -> EntityCollection:
        """Cache all entities in an iterable collection.

        Args:
            entity_cls (type[IdentifiableEntity]): The class of the entities to cache.
            collection (EntityCollection): Iterable of entities.

        Returns:
            EntityCollection: The same collection for chaining.
        """
        ns = self._resolve_ns(entity_cls)
        for entity in collection:
            self._cache[ns][entity.id] = entity
        return collection

    def clear_cache(self, namespace: str | None = None) -> None:
        """Clear cached entities to free memory.

        Expected namespaces include: 'sport', 'country', 'category', 'competition', 'season', 'event', 'competitor', 'manager', 'referee', 'venue'.

        Args:
            namespace (Optional[str]): Specific namespace to clear. If None, clears all caches.

        Raises:
            KeyError: If the provided namespace does not exist.
        """
        ns = namespace.lower() if namespace else None
        if ns:
            if ns in self._cache:
                self._cache[ns].clear()
            else:
                raise KeyError(f"Unknown cache namespace: {ns}")
        else:
            self._cache.clear()

    # --- Unified GET ---

    @overload
    def get(self, entity_cls: type[E], entity_id: str, strict: Literal[True]) -> E: ...

    @overload
    def get(self, entity_cls: type[E], entity_id: str, strict: Literal[False] = False) -> E | None: ...

    @overload
    def get(self, entity_id: str, *, strict: Literal[True]) -> IdentifiableEntity: ...

    @overload
    def get(self, entity_id: str, *, strict: Literal[False] = False) -> IdentifiableEntity | None: ...

    def get(
        self,
        entity_cls: type[E] | str | None = None,
        entity_id: str | None = None,
        strict: bool = False,
    ) -> E | IdentifiableEntity | None:
        """Fetch an identifiable entity by its ID, optionally with its class.

        Supported classes include: Sport, Competition, Event (including its subclasses),
            Competitor (including its subclasses), Manager, Referee, Venue.

        Args:
            entity_cls (type[IdentifiableEntity] | None): The class of the entity to fetch.
                Optional — if omitted, the class is resolved from the ID's own prefix.
            entity_id (str): The unique identifier of the entity.
            strict (bool): If True, raises EntityNotFoundError if the entity is not found. If False, returns None.

        Returns:
            Optional[IdentifiableEntity]: The requested entity, or None if not found.

        Raises:
            TypeError: If the entity_cls is not supported, or entity_id is missing.
            ValueError: If the entity's class can't be resolved from entity_id's prefix.
            EntityNotFoundError: If strict=True and the entity is not found.
        """
        if entity_id is None:
            if not isinstance(entity_cls, str):
                raise TypeError("entity_id is required.")
            entity_cls, entity_id = None, entity_cls

        resolved_cls = entity_cls or IdentifiableEntity.resolve_class(entity_id)
        if not issubclass(resolved_cls, IdentifiableEntity):
            raise TypeError(f"{resolved_cls.__name__} is not an identifiable entity class.")

        if cached := self._get_cached(resolved_cls, entity_id):
            return cached

        try:
            entity = resolved_cls.from_id(entity_id, self._provider)
            return self._set_cached(resolved_cls, entity)
        except EntityNotFoundError:
            if strict:
                raise
            return None

    # --- Unified SEARCH ---

    def search(self, entity_cls: type[S], query: str, max_results: int = 20) -> EntityCollection[S]:
        """
        Search for entities that implement SearchableMixin.
        """
        if not issubclass(entity_cls, SearchableMixin):
            raise TypeError(f"{entity_cls.__name__} does not support searching.")

        scored_collection = entity_cls.search(query, self._provider, max_results=max_results)
        return self._hydrate_cache(entity_cls, scored_collection.to_collection())

    # --- Unified LIST ---

    @overload
    def list(self, entity_cls: type[Sport]) -> EntityCollection[Sport]: ...

    @overload
    def list(self, entity_cls: type[Country]) -> EntityCollection[Country]: ...

    @overload
    def list(self, entity_cls: type[Category], *, sport_id: str) -> EntityCollection[Category]: ...

    @overload
    def list(self, entity_cls: type[Competition], *, category_id: str, sport_id: str | None = None) -> EntityCollection[Competition]: ...

    @overload
    def list(self, entity_cls: type[Season], *, competition_id: str) -> EntityCollection[Season]: ...

    @overload
    def list(self, entity_cls: type[Event], *, season_id: str) -> EntityCollection[Event]: ...

    def list(self, entity_cls: type[E], **kwargs: Any) -> EntityCollection[E]:
        """
        List entities of a given class with optional filters.

        Args:
            entity_cls (type[IdentifiableEntity]): The class of entities to list.
            **kwargs: Optional filters (e.g., category_id for competitions).

        Returns:
            EntityCollection[IdentifiableEntity]: A collection of entities matching the criteria.

        Raises:
            EntityNotFoundError: If additional filtering criteria are provided but no matching entities are found.
            NotImplementedError: If listing logic for the given entity class is not implemented.

        .. Warning::
            This method may rely on multiple API calls and can take a few seconds to complete on the first call.
        """
        if not issubclass(entity_cls, IdentifiableEntity):
            raise TypeError(f"{entity_cls.__name__} is not an identifiable entity class.")

        if entity_cls is Sport or entity_cls is Country:
            return self._hydrate_cache(entity_cls, entity_cls.all(self._provider))

        if entity_cls is Category:
            if "sport_id" not in kwargs:
                return self._hydrate_cache(entity_cls, entity_cls.all(self._provider))
            sport = self.get(Sport, kwargs["sport_id"], strict=True)
            return self._hydrate_cache(entity_cls, sport.categories)

        if entity_cls is Competition:
            if "category_id" not in kwargs:
                raise EntityNotFoundError("category_id is required to list competitions.")
            if "sport_id" in kwargs:
                sport = self.get(Sport, kwargs["sport_id"], strict=True)
                category = sport.categories.get(id=kwargs["category_id"], strict=True)
                return self._hydrate_cache(entity_cls, category.competitions)
            category = self.get(Category, kwargs["category_id"], strict=True)
            return self._hydrate_cache(entity_cls, category.competitions)

        if entity_cls is Season:
            if "competition_id" not in kwargs:
                raise EntityNotFoundError("competition_id is required to list seasons.")
            comp = self.get(Competition, kwargs["competition_id"], strict=True)
            return self._hydrate_cache(entity_cls, comp.seasons)

        if entity_cls is Event:
            if "season_id" not in kwargs:
                raise EntityNotFoundError("season_id is required to list events.")
            season = self.get(Season, kwargs["season_id"], strict=True)
            return self._hydrate_cache(entity_cls, season.get_events())

        # NOTE - We might implement for competitors (teams and players) in the future

        raise NotImplementedError(f"Listing logic for {entity_cls.__name__} not supported.")
