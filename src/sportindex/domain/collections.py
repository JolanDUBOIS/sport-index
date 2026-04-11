from __future__ import annotations

from collections import UserList
from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Literal, Iterable, Optional, overload

from typing_extensions import TypeVar

from .base import IdentifiableEntity
from sportindex.exceptions import EntityNotFoundError

if TYPE_CHECKING:
    from .event import Event, MatchEvent, StageEvent


I = TypeVar("I", bound="IdentifiableEntity", default="IdentifiableEntity")
I_other = TypeVar("I_other", bound="IdentifiableEntity", default="IdentifiableEntity")

# ===== Entity Collection =====

class EntityCollection(UserList[I]):
    """
    A collection of identifiable entities that supports basic list operations and provides
    additional methods for retrieving entities by attributes and searching by query. The 
    collection ensures that all entities are unique based on their IDs.

    Disabled Methods:
        append, extend, insert, __setitem__: Intentionally blocked to maintain unique sequence integrity. Use add() and update() instead.

    Methods:
        add(item: I) -> None: Add an entity to the collection if it's not already present.
        update(other: Iterable[I]) -> None: Update the collection with entities from another iterable, ensuring uniqueness.
        get(strict: bool = False, **kwargs) -> I | None: Retrieve an entity matching the given attribute filters. If strict is True, raises EntityNotFoundError if no match is found.
        search(query: str, *, by: str = "name") -> EntityCollection[I]: Search for entities where the query string is a substring of the specified attribute (default is "name").

    Raises:
        TypeError: If an item being added is not an instance of IdentifiableEntity, or if the other iterable contains invalid items.
        EntityNotFoundError: If strict is True and no matching entity is found in the get() method.
    """

    def __init__(self, initlist: Iterable[I] | None = None) -> None:
        if initlist is not None:
            items = list(initlist)
            self._validate_iterable(items)
            super().__init__(dict.fromkeys(items))
        else:
            super().__init__()

    def _validate_item(self, item: Any) -> None:
        if not isinstance(item, IdentifiableEntity):
            raise TypeError(f"Expected IdentifiableEntity, got {type(item).__name__}")

    def _validate_iterable(self, items: Iterable[Any]) -> None:
        for item in items:
            self._validate_item(item)

    def add(self, item: I) -> None:
        self._validate_item(item)
        if item not in self.data:
            self.data.append(item)

    def update(self, other: Iterable[I]) -> None:
        other_items = other.data if isinstance(other, UserList) else list(other)
        self._validate_iterable(other_items)
        self.data = list(dict.fromkeys(self.data + other_items))

    def append(self, item: I) -> None:
        raise NotImplementedError("Use .add() to add entities to a unique collection.")

    def extend(self, other: Iterable[I]) -> None:
        raise NotImplementedError("Use .update() to merge iterable entities into a unique collection.")

    def insert(self, i: int, item: I) -> None:
        raise NotImplementedError("Direct insertion is disabled to maintain unique sequence integrity.")

    def __setitem__(self, i: int | slice, item: Any) -> None:
        raise NotImplementedError("Index assignment is disabled to maintain unique sequence integrity.")

    @overload
    def __add__(self, other: EntityCollection[I_other] | Iterable[I_other]) -> EntityCollection[I | I_other]: ...

    def __add__(self, other: Any) -> Any:
        if not isinstance(other, Iterable) or isinstance(other, (str, bytes)):
            return NotImplemented
        other_items = other.data if isinstance(other, UserList) else list(other)
        self._validate_iterable(other_items)
        merged = list(dict.fromkeys(self.data + other_items))
        return self.__class__(merged)

    @overload
    def __iadd__(self, other: EntityCollection[I_other] | Iterable[I_other]) -> EntityCollection[I | I_other]: ...

    def __iadd__(self, other: Any) -> Any:
        if not isinstance(other, Iterable) or isinstance(other, (str, bytes)):
            return NotImplemented
        self.update(other)
        return self

    @overload
    def get(self, *, strict: Literal[True], **kwargs: Any) -> I: ...

    @overload
    def get(self, *, strict: Literal[False] = False, **kwargs: Any) -> I | None: ...

    def get(self, *, strict: bool = False, **kwargs: Any) -> I | None:
        """
        Retrieve an entity from the collection that matches the given attribute filters.

        Args:
            strict (bool): If True, raises EntityNotFoundError if no matching entity is found. If False, returns None instead.
            **kwargs: Attribute filters to match against the entities in the collection.
        
        Returns:
            I | None: The matching entity if found, otherwise None (if strict is False).

        Raises:
            EntityNotFoundError: If strict is True and no matching entity is found.

        Example:
            manager = managers.get(id=123, strict=True)  # Raises if not found
        """
        for e in self.data:
            if all(getattr(e, k, None) == v for k, v in kwargs.items()):
                return e

        if strict:
            filter_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            raise EntityNotFoundError(f"No entity found matching: {filter_str}")

        return None

    def search(self, query: str, *, by: str = "name") -> EntityCollection[I]:
        """
        Search for entities in the collection where the query string is a substring of the specified attribute.

        Args:
            query (str): The search query string.
            by (str): The attribute name to search by (default is "name").

        Returns:
            EntityCollection[I]: A new collection containing entities that match the search query.

        Example:
            results = managers.search("zidane")  # Searches by name by default
        """
        clean_query = query.strip().lower()
        results = [
            e for e in self.data
            if clean_query in str(getattr(e, by, "")).lower()
        ]
        return self.__class__(results)


# ===== Scored Entity Collection =====

class ScoredEntityCollection(EntityCollection[I]):
    """
    A read-only collection of entities resulting from a scored operation (like a search).
    Behaves exactly like a standard EntityCollection during iteration and indexing, 
    but internally tracks scores to allow for score-based filtering and sorting.

    If multiple score entries for the same entity are provided during initialization,
    the highest score is retained.

    Disabled Methods:
        add, update, append, extend, insert, __setitem__, __add__, __iadd__:
        Blocked to maintain the read-only integrity of the search results.

    Methods:
        get_score(entity_id: int) -> float: Retrieve the score for a specific entity ID in the collection.
        sort_by_score(descending: bool = True) -> ScoredEntityCollection[I]: Return a new collection sorted by the internal scores.
        filter_by_score(min_score: float | None = None, max_score: float | None = None) -> ScoredEntityCollection[I]: Return a new collection filtered by a score range.
        merge(*collections: ScoredEntityCollection[IdentifiableEntity]) -> ScoredEntityCollection[IdentifiableEntity]: Internal helper to merge multiple ScoredEntityCollections, retaining the highest scores for duplicate entities.

    Raises:
        ValueError: If get_score is called with an entity ID that is not in the collection.
        NotImplementedError: If any of the disabled modification methods are called.
    """

    def __init__(self, items_with_scores: Iterable[tuple[I, float]] | None = None) -> None:
        self._scores: dict[int, float] = {}
        unique_entities: dict[int, I] = {}

        if items_with_scores is not None:
            for entity, score in items_with_scores:
                if not isinstance(entity, IdentifiableEntity):
                    raise TypeError(f"Expected IdentifiableEntity, got {type(entity).__name__}")

                if entity.id not in self._scores or score > self._scores[entity.id]:
                    self._scores[entity.id] = score

                if entity.id not in unique_entities:
                    unique_entities[entity.id] = entity

            super().__init__(unique_entities.values())
        else:
            super().__init__()

    def get_score(self, entity_id: int) -> float:
        """Retrieve the score for a specific entity ID in the collection."""
        if entity_id not in self._scores:
            raise ValueError(f"Entity ID {entity_id} not found in this scored collection.")
        return self._scores[entity_id]

    def sort_by_score(self, descending: bool = True) -> ScoredEntityCollection[I]:
        """Return a new collection sorted by the internal scores."""
        sorted_pairs = sorted(
            [(e, self._scores[e.id]) for e in self.data],
            key=lambda x: x[1],
            reverse=descending
        )
        return self.__class__(sorted_pairs)

    def filter_by_score(self, min_score: float | None = None, max_score: float | None = None) -> ScoredEntityCollection[I]:
        """Return a new collection filtered by a score range."""
        filtered_pairs = []
        for e in self.data:
            score = self._scores[e.id]
            if min_score is not None and score < min_score:
                continue
            if max_score is not None and score > max_score:
                continue
            filtered_pairs.append((e, score))
            
        return self.__class__(filtered_pairs)

    def to_collection(self) -> EntityCollection[I]:
        """Convert this scored collection to a standard EntityCollection, discarding scores."""
        return EntityCollection(self.data)

    @overload
    def __getitem__(self, i: int) -> I: ...

    @overload
    def __getitem__(self, i: slice) -> ScoredEntityCollection[I]: ...

    def __getitem__(self, i: int | slice) -> I | ScoredEntityCollection[I]:
        if isinstance(i, slice):
            return self.__class__([(e, self._scores[e.id]) for e in self.data[i]])
        return self.data[i]

    def add(self, item: Any) -> None:
        raise NotImplementedError("ScoredEntityCollection is read-only.")

    def update(self, other: Any) -> None:
        raise NotImplementedError("ScoredEntityCollection is read-only.")

    def __add__(self, other: Any) -> Any:
        raise NotImplementedError("ScoredEntityCollection is read-only.")

    def __iadd__(self, other: Any) -> Any:
        raise NotImplementedError("ScoredEntityCollection is read-only.")

    def search(self, query, *, by = "name") -> Any:
        raise NotImplementedError("ScoredEntityCollection does not support search operations.")

    @classmethod
    def merge(cls, *collections: ScoredEntityCollection[IdentifiableEntity]) -> ScoredEntityCollection[IdentifiableEntity]:
        """
        Internal helper to merge multiple ScoredEntityCollections.
        Highest scores for duplicate entities across collections are retained.
        """
        merged_items: list[tuple[IdentifiableEntity, float]] = []
        for col in collections:
            merged_items.extend((e, col.get_score(e.id)) for e in col.data)
        
        return cls(merged_items)


# ===== Event Collection =====

E = TypeVar("E", bound="Event", default="Event")

class EventCollection(EntityCollection[E]):
    """
    A specialized collection for handling lists of events with common filtering and sorting needs.
    Inherits uniqueness enforcement and attribute querying from EntityCollection.
    """

    @property
    def matches(self) -> EventCollection[MatchEvent]:
        """Return a new EventCollection containing only match events."""
        from .event import MatchEvent
        return EventCollection([e for e in self.data if isinstance(e, MatchEvent)])

    @property
    def stages(self) -> EventCollection[StageEvent]:
        """Return a new EventCollection containing only stage events."""
        from .event import StageEvent
        return EventCollection([e for e in self.data if isinstance(e, StageEvent)])

    def filter_by_date(self, *, before: Optional[date | datetime] = None, after: Optional[date | datetime] = None) -> EventCollection[E]:
        """Return a new EventCollection filtered by date."""
        results = self.data

        def to_dt(val: date | datetime) -> datetime:
            if isinstance(val, datetime): 
                return val
            return datetime.combine(val, datetime.min.time())

        if before is not None:
            before_dt = to_dt(before)
            results = [e for e in results if e.start < before_dt]
        if after is not None:
            after_dt = to_dt(after)
            results = [e for e in results if e.start > after_dt]

        return self.__class__(results)

    def sort_by_date(self, ascending: bool = True) -> EventCollection[E]:
        """Return a new EventCollection sorted by date."""
        return self.__class__(sorted(self.data, key=lambda e: e.start, reverse=not ascending))

    def filter_by_competitors(self, competitor_ids: list[int]) -> EventCollection[MatchEvent]:
        """Return a new EventCollection containing only match events involving the specified competitor IDs."""
        results = []
        for event in self.matches:
            if event.competitors and ((event.competitors.home.id in competitor_ids) or (event.competitors.away.id in competitor_ids)):
                results.append(event)
        return EventCollection(results)
