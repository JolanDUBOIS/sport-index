from __future__ import annotations

import os
import logging
from typing import Optional, TypeVar, Any, Iterable

from .domain import (
    get_sports,
    BaseEntity,
    Category,
    Competition,
    Competitor,
    EntityCollection,
    Event,
    Manager,
    Referee,
    Season,
    Sport,
    Venue
)
from .exceptions import ProviderNotFoundError, EntityNotFoundError
from .provider import SofascoreProvider, Fetcher, RecordingFetcher


logger = logging.getLogger(__name__)
_default_provider = None

def _get_default_provider() -> SofascoreProvider:
    global _default_provider
    if _default_provider is None:
        record_mode = os.getenv("SPORTINDEX_RECORD_MODE")
        fixtures_dir = os.getenv("SPORTINDEX_FIXTURES_DIR", "tests/fixtures")

        if record_mode in ("record", "replay"):
            logger.info(f"Initialized SportClient in testing mode: '{record_mode}' (Dir: {fixtures_dir})")
            fetcher = RecordingFetcher(mode=record_mode, cache_dir=fixtures_dir)
        else:
            logger.info("Initialized SportClient in standard LIVE mode.")
            fetcher = Fetcher()

        _default_provider = SofascoreProvider(fetcher=fetcher)
    return _default_provider


T = TypeVar("T", bound=BaseEntity)
C = TypeVar("C", bound=Iterable[BaseEntity])

class SportClient:
    """Main client for accessing sports data.

    Provides methods to fetch sports, competitions, events, competitors, managers, referees, venues, etc. in a unified, object-oriented way.
    Caches entities in memory to minimize redundant API calls and improve performance. Cache can be cleared manually if needed.

    Usage:
        >>> client = SportClient()
        >>> events = client.list_events(competition_id=123)
        >>> sport = client.get_sport(id=1)

    Raises:
        EntityNotFoundError: If a requested entity does not exist.
        ProviderNotFoundError: If the data provider is unavailable.
    """

    def __init__(self):
        """Initialize the SportClient.

        Initializes in-memory caches for all entity types.
        """
        self._provider = _get_default_provider()

        self._cache: dict[str, dict[int, Any]] = {
            "sports": {}, 
            "competitions": {},
            "seasons": {},
            "events": {},
            "competitors": {},
            "managers": {},
            "referees": {},
            "venues": {},
        }

    # --- Cache Helpers ---

    def _get_cached(self, namespace: str, entity_id: int, expected_type: type[T]) -> Optional[T]:
        """Return an entity from the cache if it exists.

        Args:
            namespace (str): The cache namespace (e.g., 'events', 'competitions').
            entity_id (int): The unique identifier of the entity.
            expected_type (type[T]): Expected type of the entity for IDE type hinting.

        Returns:
            Optional[T]: The cached entity, or None if not found.
        """
        return self._cache[namespace].get(entity_id)

    def _set_cached(self, namespace: str, entity: T) -> T:
        """Add an entity to the cache and return it.

        Args:
            namespace (str): The cache namespace.
            entity (T): The entity to store.

        Returns:
            T: The same entity for chaining.
        """
        self._cache[namespace][entity.id] = entity
        return entity

    def _hydrate_cache(self, namespace: str, collection: C) -> C:
        """Cache all entities in an iterable collection.

        Args:
            namespace (str): The cache namespace.
            collection (C): Iterable of entities.

        Returns:
            C: The same collection for chaining.
        """
        for entity in collection:
            self._cache[namespace][entity.id] = entity
        return collection

    def clear_cache(self, namespace: Optional[str] = None) -> None:
        """Clear cached entities to free memory.

        Args:
            namespace (Optional[str]): Specific namespace to clear. If None, clears all caches.

        Raises:
            KeyError: If the provided namespace does not exist.
        """
        if namespace:
            if namespace in self._cache:
                self._cache[namespace].clear()
            else:
                raise KeyError(f"Unknown cache namespace: {namespace}")
        else:
            for ns in self._cache:
                self._cache[ns].clear()

    # --- Sports ---

    def get_sport(self, id: int) -> Sport | None:
        """Fetch a sport by its ID.

        Args:
            id (int): The sport ID.

        Returns:
            Optional[Sport]: The sport object, or None if not found.
        """
        sports = self.list_sports()
        return sports.get(id=id)

    def list_sports(self) -> EntityCollection[Sport]:
        """Return all known sports.

        Returns:
            EntityCollection[Sport]: All sports available.
        """
        sports = get_sports()
        return self._hydrate_cache("sports", sports)

    def search_sports(self, query: str) -> EntityCollection[Sport]:
        """Search for sports matching a query.

        Args:
            query (str): Partial or full sport name.

        Returns:
            EntityCollection[Sport]: Sports that match the query.
        """
        sports = self.list_sports()
        return sports.search(query)

    # --- Categories ---

    def list_categories(self, sport_id: int) -> EntityCollection[Category]:
        """Fetch categories for a given sport.

        Args:
            sport_id (int): The ID of the sport.

        Returns:
            EntityCollection[Category]: Categories under the sport.

        Raises:
            EntityNotFoundError: If the sport does not exist.
        """
        sport = self.get_sport(sport_id)
        if sport is None:
            raise EntityNotFoundError(f"Sport with ID {sport_id} not found")
        return sport.categories

    # --- Competitions ---

    def get_competition(self, id: int) -> Optional[Competition]:
        """Fetch a competition by ID.

        Args:
            id (int): Competition ID.

        Returns:
            Optional[Competition]: The competition if found, else None.

        Raises:
            ProviderNotFoundError: If the data provider is unavailable.
        """
        if cached := self._get_cached("competitions", id, Competition):
            return cached
        try:
            entity = Competition.from_id(id, self._provider)
            return self._set_cached("competitions", entity)
        except ProviderNotFoundError:
            return None

    def list_competitions(self, sport_id: int, category_id: int) -> EntityCollection[Competition]:
        """Fetch competitions for a sport and category.

        Args:
            sport_id (int): Sport ID.
            category_id (int): Category ID.

        Returns:
            EntityCollection[Competition]: Competitions under the category.

        Raises:
            EntityNotFoundError: If sport or category does not exist.
        """
        sport = self.get_sport(sport_id)
        if sport is None:
            raise EntityNotFoundError(f"Sport with ID {sport_id} not found")
        category = sport.categories.get(id=category_id)
        if category is None:
            raise EntityNotFoundError(f"Category with ID {category_id} not found")
        return self._hydrate_cache("competitions", category.competitions)

    # --- Seasons ---

    def list_seasons(self, competition_id: int) -> EntityCollection[Season]:
        """Fetch seasons for a competition.

        Args:
            competition_id (int): Competition ID.

        Returns:
            EntityCollection[Season]: Seasons under the competition.

        Raises:
            EntityNotFoundError: If the competition does not exist.
        """
        competition = self.get_competition(competition_id)
        if competition is None:
            raise EntityNotFoundError(f"Competition with ID {competition_id} not found")
        return self._hydrate_cache("seasons", competition.seasons)

    # --- Events ---

    def get_event(self, id: int) -> Optional[Event]:
        """Fetch an event by ID.

        Args:
            id (int): Event ID.

        Returns:
            Optional[Event]: Event object if found, else None.

        Raises:
            ProviderNotFoundError: If the provider is unavailable.
        """
        if cached := self._get_cached("events", id, Event):
            return cached
        try:
            entity = Event.from_id(id, self._provider)
            return self._set_cached("events", entity)
        except ProviderNotFoundError:
            return None

    # --- Competitors ---

    def get_competitor(self, id: int) -> Optional[Competitor]:
        """Fetch a competitor by ID.

        Args:
            id (int): Competitor ID.

        Returns:
            Optional[Competitor]: Competitor if found, else None.

        Raises:
            ProviderNotFoundError: If the provider is unavailable.
        """
        if cached := self._get_cached("competitors", id, Competitor):
            return cached
        try:
            entity = Competitor.from_id(id, self._provider)
            return self._set_cached("competitors", entity)
        except ProviderNotFoundError:
            return None

    def search_competitors(self, query: str) -> EntityCollection[Competitor]:
        """Search for competitors by name.

        Args:
            query (str): Partial or full competitor name.

        Returns:
            EntityCollection[Competitor]: Matching competitors.
        """
        results = Competitor.search(query, self._provider)
        return self._hydrate_cache("competitors", results)

    # --- Managers ---

    def get_manager(self, id: int) -> Optional[Manager]:
        """Fetch a manager by ID.

        Args:
            id (int): Manager ID.

        Returns:
            Optional[Manager]: Manager if found, else None.

        Raises:
            ProviderNotFoundError: If the provider is unavailable.
        """
        if cached := self._get_cached("managers", id, Manager):
            return cached
        try:
            entity = Manager.from_id(id, self._provider)
            return self._set_cached("managers", entity)
        except ProviderNotFoundError:
            return None

    def search_managers(self, query: str) -> EntityCollection[Manager]:
        """Search for managers by name.

        Args:
            query (str): Partial or full manager name.

        Returns:
            EntityCollection[Manager]: Matching managers.
        """
        results = Manager.search(query, self._provider)
        return self._hydrate_cache("managers", results)

    # --- Referees ---

    def get_referee(self, id: int) -> Optional[Referee]:
        """Fetch a referee by ID.

        Args:
            id (int): Referee ID.

        Returns:
            Optional[Referee]: Referee if found, else None.

        Raises:
            ProviderNotFoundError: If the provider is unavailable.
        """
        if cached := self._get_cached("referees", id, Referee):
            return cached
        try:
            entity = Referee.from_id(id, self._provider)
            return self._set_cached("referees", entity)
        except ProviderNotFoundError:
            return None

    def search_referees(self, query: str) -> EntityCollection[Referee]:
        """Search referees by name.

        Args:
            query (str): Partial or full referee name.

        Returns:
            EntityCollection[Referee]: Matching referees.
        """
        results = Referee.search(query, self._provider)
        return self._hydrate_cache("referees", results)

    # --- Venues ---

    def get_venue(self, id: int) -> Optional[Venue]:
        """Fetch a venue by ID.

        Args:
            id (int): Venue ID.

        Returns:
            Optional[Venue]: Venue if found, else None.

        Raises:
            ProviderNotFoundError: If the provider is unavailable.
        """
        if cached := self._get_cached("venues", id, Venue):
            return cached
        try:
            entity = Venue.from_id(id, self._provider)
            return self._set_cached("venues", entity)
        except ProviderNotFoundError:
            return None

    def search_venues(self, query: str) -> EntityCollection[Venue]:
        """Search venues by name.

        Args:
            query (str): Partial or full venue name.

        Returns:
            EntityCollection[Venue]: Matching venues.
        """
        results = Venue.search(query, self._provider)
        return self._hydrate_cache("venues", results)