from __future__ import annotations

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
from .provider import ParsedSofascoreProvider, NotFoundError


_default_provider = None

def _get_default_provider() -> ParsedSofascoreProvider:
    global _default_provider
    if _default_provider is None:
        _default_provider = ParsedSofascoreProvider()
    return _default_provider


T = TypeVar("T", bound=BaseEntity)
C = TypeVar("C", bound=Iterable[BaseEntity])

class SportClient:

    def __init__(self, provider: Optional[ParsedSofascoreProvider] = None):
        self._provider = provider or _get_default_provider()

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
        """Check if an entity exists in the cache. The expected_type is used for strict IDE type hinting."""
        return self._cache[namespace].get(entity_id)

    def _set_cached(self, namespace: str, entity: T) -> T:
        """Add an entity to the cache and return it for easy chaining."""
        self._cache[namespace][entity.id] = entity
        return entity

    def _hydrate_cache(self, namespace: str, collection: C) -> C:
        """Takes an iterable of entities, caches them all, and returns the collection seamlessly."""
        for entity in collection:
            self._cache[namespace][entity.id] = entity
        return collection

    def clear_cache(self, namespace: Optional[str] = None) -> None:
        """
        Clears the stored entities to free up memory.
        If a namespace (e.g., 'events') is provided, clears only that section.
        """
        if namespace:
            if namespace in self._cache:
                self._cache[namespace].clear()
            else:
                raise ValueError(f"Unknown cache namespace: {namespace}")
        else:
            for ns in self._cache:
                self._cache[ns].clear()

    # --- Sports ---

    def get_sport(self, id: int) -> Sport | None:
        """Fetch a sport by its ID."""
        sports = self.list_sports()
        return sports.get(id=id)

    def list_sports(self) -> EntityCollection[Sport]:
        """Return the list of known sports."""
        sports = get_sports()
        return self._hydrate_cache("sports", sports)

    def search_sports(self, query: str) -> EntityCollection[Sport]:
        """Search for sports matching the given query."""
        sports = self.list_sports()
        return sports.search(query)

    # --- Categories ---

    def list_categories(self, sport_id: int) -> EntityCollection[Category]:
        """Fetch categories for a given sport ID."""
        sport = self.get_sport(sport_id)
        if sport is None:
            raise ValueError(f"Sport with ID {sport_id} not found")
        return sport.categories

    # --- Competitions ---

    def get_competition(self, id: int) -> Optional[Competition]:
        """Fetch a competition by its ID."""
        if cached := self._get_cached("competitions", id, Competition):
            return cached
        try:
            entity = Competition.from_id(id, self._provider)
            return self._set_cached("competitions", entity)
        except NotFoundError:
            return None

    def list_competitions(self, sport_id: int, category_id: int) -> EntityCollection[Competition]:
        """Fetch competitions for a given sport ID and category ID."""
        sport = self.get_sport(sport_id)
        if sport is None:
            raise ValueError(f"Sport with ID {sport_id} not found")
        category = sport.categories.get(id=category_id)
        if category is None:
            raise ValueError(f"Category with ID {category_id} not found")
        
        return self._hydrate_cache("competitions", category.competitions)

    # --- Seasons ---

    def list_seasons(self, competition_id: int) -> EntityCollection[Season]:
        """Fetch seasons for a given competition ID."""
        competition = self.get_competition(competition_id)
        if competition is None:
            raise ValueError(f"Competition with ID {competition_id} not found")
        return self._hydrate_cache("seasons", competition.seasons)

    # --- Events ---

    def get_event(self, id: int) -> Optional[Event]:
        """Fetch an event by its ID."""
        if cached := self._get_cached("events", id, Event):
            return cached
        try:
            entity = Event.from_id(id, self._provider)
            return self._set_cached("events", entity)
        except NotFoundError:
            return None

    # --- Competitors ---

    def get_competitor(self, id: int) -> Optional[Competitor]:
        """Fetch a competitor by its ID."""
        if cached := self._get_cached("competitors", id, Competitor):
            return cached
        try:
            entity = Competitor.from_id(id, self._provider)
            return self._set_cached("competitors", entity)
        except NotFoundError:
            return None

    def search_competitors(self, query: str) -> EntityCollection[Competitor]:
        """Search for competitors matching the given query."""
        results = Competitor.search(query, self._provider)
        return self._hydrate_cache("competitors", results)

    # --- Managers ---

    def get_manager(self, id: int) -> Optional[Manager]:
        """Fetch a manager by its ID."""
        if cached := self._get_cached("managers", id, Manager):
            return cached
        try:
            entity = Manager.from_id(id, self._provider)
            return self._set_cached("managers", entity)
        except NotFoundError:
            return None

    def search_managers(self, query: str) -> EntityCollection[Manager]:
        """Search for managers matching the given query."""
        results = Manager.search(query, self._provider)
        return self._hydrate_cache("managers", results)

    # --- Referees ---

    def get_referee(self, id: int) -> Optional[Referee]:
        """Fetch a referee by its ID."""
        if cached := self._get_cached("referees", id, Referee):
            return cached
        try:
            entity = Referee.from_id(id, self._provider)
            return self._set_cached("referees", entity)
        except NotFoundError:
            return None

    def search_referees(self, query: str) -> EntityCollection[Referee]:
        """Search for referees matching the given query."""
        results = Referee.search(query, self._provider)
        return self._hydrate_cache("referees", results)

    # --- Venues ---

    def get_venue(self, id: int) -> Optional[Venue]:
        """Fetch a venue by its ID."""
        if cached := self._get_cached("venues", id, Venue):
            return cached
        try:
            entity = Venue.from_id(id, self._provider)
            return self._set_cached("venues", entity)
        except NotFoundError:
            return None

    def search_venues(self, query: str) -> EntityCollection[Venue]:
        """Search for venues matching the given query."""
        results = Venue.search(query, self._provider)
        return self._hydrate_cache("venues", results)