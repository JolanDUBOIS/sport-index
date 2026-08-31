from __future__ import annotations

from collections import UserList
from collections.abc import Iterable
from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Any, Literal, overload

from typing_extensions import TypeVar

from sportindex.exceptions import EntityNotFoundError

from .base import IdentifiableEntity

if TYPE_CHECKING:
    from .event import Event, MatchEvent, StageEvent


#: How many entities a collection's repr previews before summarising the rest as a count.
_REPR_PREVIEW = 3

EntityT = TypeVar("EntityT", bound="IdentifiableEntity", default="IdentifiableEntity")
OtherEntityT = TypeVar("OtherEntityT", bound="IdentifiableEntity", default="IdentifiableEntity")

# ===== Entity Collection =====

class EntityCollection(UserList[EntityT]):
    """An ordered, duplicate-free list of entities.

    Behaves as a list — index it, slice it, iterate it, take its length — while guaranteeing
    that no entity appears twice and that insertion order is preserved. Two entities count as
    the same when they share a type and an SDK ID. This is how the domain hands back groups
    of addressable entities; plain values such as standings rows come back as ordinary lists.
    The in-place list mutators are disabled in favour of `add()` and `update()`, which enforce
    uniqueness; the set operators build new collections rather than mutating.

    Methods:
        add(item: EntityT) -> None: Append `item` unless an equal entity is already present.
        update(other: Iterable[EntityT]) -> None: Merge `other` in, keeping first occurrences.
        get(*, strict: bool = False, **kwargs) -> EntityT | None: The first entity whose
            attributes all match the given keyword filters, e.g. `get(name="Ligue 1")`. None
            when nothing matches, unless `strict` is True.
        search(query: str, *, by: str = "name") -> EntityCollection[EntityT]: A new collection
            of the entities whose `by` attribute contains `query`, case-insensitively.
        __add__(other) / __or__(other) -> EntityCollection: A new collection holding this one's
            entities followed by `other`'s, duplicates dropped.
        __and__(other) -> EntityCollection: A new collection holding only the entities present
            in both, in this collection's order.

    Disabled Methods:
        append, extend, insert, __setitem__: Raise NotImplementedError, since they would let
            duplicates in. Use `add()` and `update()` instead.

    Raises:
        TypeError: If an entity being added is not an `IdentifiableEntity`.
        EntityNotFoundError: If `get(strict=True)` matches nothing.
        NotImplementedError: If a disabled mutator is called.
    """

    def __init__(self, initlist: Iterable[EntityT] | None = None) -> None:
        if initlist is not None:
            items = list(initlist)
            self._validate_iterable(items)
            super().__init__(dict.fromkeys(items))
        else:
            super().__init__()

    def __repr__(self) -> str:
        """A summary, not a dump.

        A collection routinely holds hundreds of entities, each of which would otherwise
        expand in full. Showing a count and the first few keeps the output readable in a
        REPL, where printing a collection is the most common way to look at one.
        """
        if not self.data:
            return f"<{type(self).__name__} empty>"

        preview = ", ".join(self._repr_item(item) for item in self.data[:_REPR_PREVIEW])
        remainder = len(self.data) - _REPR_PREVIEW
        if remainder > 0:
            preview += f", +{remainder} more"
        return f"<{type(self).__name__} {len(self.data)} items: {preview}>"

    def _repr_item(self, item: EntityT) -> str:
        """One entity, as it appears in the collection's preview."""
        return item._repr_token()

    def _validate_item(self, item: Any) -> None:
        if not isinstance(item, IdentifiableEntity):
            raise TypeError(f"Expected IdentifiableEntity, got {type(item).__name__}")

    def _validate_iterable(self, items: Iterable[Any]) -> None:
        for item in items:
            self._validate_item(item)

    def add(self, item: EntityT) -> None:
        """Append an entity to the collection unless an equal one is already present."""
        self._validate_item(item)
        if item not in self.data:
            self.data.append(item)

    def update(self, other: Iterable[EntityT]) -> None:
        """Merge entities from another iterable in, keeping the first occurrence of each."""
        other_items = other.data if isinstance(other, UserList) else list(other)
        self._validate_iterable(other_items)
        self.data = list(dict.fromkeys(self.data + other_items))

    def append(self, item: EntityT) -> None:
        """Disabled — use add(), which enforces uniqueness."""
        raise NotImplementedError("Use .add() to add entities to a unique collection.")

    def extend(self, other: Iterable[EntityT]) -> None:
        """Disabled — use update(), which enforces uniqueness."""
        raise NotImplementedError("Use .update() to merge iterable entities into a unique collection.")

    def insert(self, i: int, item: EntityT) -> None:
        """Disabled — positional insertion cannot preserve uniqueness."""
        raise NotImplementedError("Direct insertion is disabled to maintain unique sequence integrity.")

    def __setitem__(self, i: int | slice, item: Any) -> None:
        raise NotImplementedError("Index assignment is disabled to maintain unique sequence integrity.")

    @overload
    def __add__(self, other: EntityCollection[OtherEntityT] | Iterable[OtherEntityT]) -> EntityCollection[EntityT | OtherEntityT]: ...

    def __add__(self, other: Any) -> Any:
        if not isinstance(other, Iterable) or isinstance(other, (str, bytes)):
            return NotImplemented
        other_items = other.data if isinstance(other, UserList) else list(other)
        self._validate_iterable(other_items)
        merged = list(dict.fromkeys(self.data + other_items))
        return self.__class__(merged)

    @overload
    def __or__(self, other: EntityCollection[OtherEntityT] | Iterable[OtherEntityT]) -> EntityCollection[EntityT | OtherEntityT]: ...

    def __or__(self, other: Any) -> Any:
        if not isinstance(other, Iterable) or isinstance(other, (str, bytes)):
            return NotImplemented
        other_items = other.data if isinstance(other, UserList) else list(other)
        self._validate_iterable(other_items)
        return self.__class__(dict.fromkeys(self.data + other_items))

    @overload
    def __and__(self, other: EntityCollection[OtherEntityT] | Iterable[OtherEntityT]) -> EntityCollection[EntityT | OtherEntityT]: ...

    def __and__(self, other: Any) -> Any:
        if not isinstance(other, Iterable) or isinstance(other, (str, bytes)):
            return NotImplemented
        other_items = set(other.data if isinstance(other, UserList) else list(other))
        self._validate_iterable(other_items)
        return self.__class__([item for item in self.data if item in other_items])

    @overload
    def get(self, *, strict: Literal[True], **kwargs: Any) -> EntityT: ...

    @overload
    def get(self, *, strict: Literal[False] = False, **kwargs: Any) -> EntityT | None: ...

    def get(self, *, strict: bool = False, **kwargs: Any) -> EntityT | None:
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

    def search(self, query: str, *, by: str = "name") -> EntityCollection[EntityT]:
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

class ScoredEntityCollection(EntityCollection[EntityT]):
    """A read-only `EntityCollection` whose entities each carry a relevance score.

    What every `search()` returns. Iterating and indexing it yields plain entities, exactly
    as with an `EntityCollection`; the scores sit alongside and drive `sort_by_score()` and
    `filter_by_score()`. Where the same entity arrives more than once, its highest score
    wins. The collection is immutable — build a new one instead of changing this one, or call
    `to_collection()` to drop the scores.

    Methods:
        get_score(entity_id: str) -> float: The score recorded for that entity's SDK ID.
        sort_by_score(descending: bool = True) -> ScoredEntityCollection[EntityT]: A new
            collection ordered by score, best first by default.
        filter_by_score(min_score: float | None = None, max_score: float | None = None) -> ScoredEntityCollection[EntityT]:
            A new collection holding only the entities whose score falls within the bounds
            given; an omitted bound is unbounded.
        to_collection() -> EntityCollection[EntityT]: The same entities in the same order as a
            plain, mutable `EntityCollection`, scores discarded.
        merge(*collections: ScoredEntityCollection[IdentifiableEntity]) -> ScoredEntityCollection[IdentifiableEntity]:
            One collection holding every entity across the inputs, each keeping its highest
            score. (classmethod)

    Disabled Methods:
        add, update, append, extend, insert, __setitem__, __add__, __or__, __and__, search:
            Raise NotImplementedError — the collection is read-only, and `search` would drop
            the scores.

    Raises:
        TypeError: If an entity is not an `IdentifiableEntity`.
        ValueError: If `get_score` is given an ID the collection does not hold.
        NotImplementedError: If a disabled method is called.
    """

    def __init__(self, items_with_scores: Iterable[tuple[EntityT, float]] | None = None) -> None:
        self._scores: dict[str, float] = {}
        unique_entities: dict[str, EntityT] = {}

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

    def _repr_item(self, item: EntityT) -> str:
        """One entity and the score it carries, which is the point of this collection."""
        return f"{item._repr_token()} ({self._scores[item.id]:.2f})"

    def get_score(self, entity_id: str) -> float:
        """Retrieve the score for a specific entity ID in the collection."""
        if entity_id not in self._scores:
            raise ValueError(f"Entity ID {entity_id} not found in this scored collection.")
        return self._scores[entity_id]

    def sort_by_score(self, descending: bool = True) -> ScoredEntityCollection[EntityT]:
        """Return a new collection sorted by the internal scores."""
        sorted_pairs = sorted(
            [(e, self._scores[e.id]) for e in self.data],
            key=lambda x: x[1],
            reverse=descending
        )
        return self.__class__(sorted_pairs)

    def filter_by_score(self, min_score: float | None = None, max_score: float | None = None) -> ScoredEntityCollection[EntityT]:
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

    def to_collection(self) -> EntityCollection[EntityT]:
        """Convert this scored collection to a standard EntityCollection, discarding scores."""
        return EntityCollection(self.data)

    @overload
    def __getitem__(self, i: int) -> EntityT: ...

    @overload
    def __getitem__(self, i: slice) -> ScoredEntityCollection[EntityT]: ...

    def __getitem__(self, i: int | slice) -> EntityT | ScoredEntityCollection[EntityT]:
        if isinstance(i, slice):
            return self.__class__([(e, self._scores[e.id]) for e in self.data[i]])
        return self.data[i]

    def add(self, item: Any) -> None:
        """Disabled — a scored collection is read-only."""
        raise NotImplementedError("ScoredEntityCollection is read-only.")

    def update(self, other: Any) -> None:
        """Disabled — a scored collection is read-only."""
        raise NotImplementedError("ScoredEntityCollection is read-only.")

    def __add__(self, other: Any) -> Any:
        raise NotImplementedError("ScoredEntityCollection is read-only.")

    def __or__(self, other: Any) -> Any:
        raise NotImplementedError("ScoredEntityCollection is read-only.")

    def __and__(self, other: Any) -> Any:
        raise NotImplementedError("ScoredEntityCollection is read-only.")

    def search(self, query, *, by = "name") -> Any:
        """Disabled — filtering a scored collection this way would discard its scores."""
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
    """An `EntityCollection` of events, with the filters a calendar needs.

    Everything `EntityCollection` offers applies here too; the members below are what an
    event collection adds. All of them return new collections rather than filtering in place.
    A collection may mix `MatchEvent` and `StageEvent` — a channel's schedule does — which is
    what `matches` and `stages` are for.

    Attributes:
        matches (EventCollection[MatchEvent]): Only the match events.
        stages (EventCollection[StageEvent]): Only the stage events.

    A `StageEvent` may have no `start`, so both date methods say what they do with one: a
    date filter drops undated events, and a date sort puts them last.

    Methods:
        filter_by_date(*, before: date | datetime | None = None, after: date | datetime | None = None) -> EventCollection[E]:
            Only the events starting strictly before `before` and strictly after `after`. A
            bare date counts as midnight at its start. An omitted bound is unbounded. Undated
            events satisfy no bound and are dropped whenever one is given.
        sort_by_date(ascending: bool = True) -> EventCollection[E]: The same events ordered by
            start time, oldest first by default, with undated events last in either direction.
        filter_by_competitors(competitor_ids: list[str]) -> EventCollection[MatchEvent]: Only
            the match events with one of the given competitor SDK IDs on either side. Stage
            events are dropped, having no two named sides.
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

    def filter_by_date(self, *, before: date | datetime | None = None, after: date | datetime | None = None) -> EventCollection[E]:
        """Return a new EventCollection filtered by date."""
        results = self.data

        def to_dt(val: date | datetime) -> datetime:
            # Event.start is always UTC-aware, so a bare date — or a naive datetime — has to
            # be anchored to UTC before it can be compared against one.
            dt = val if isinstance(val, datetime) else datetime.combine(val, datetime.min.time())
            return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)

        if before is not None:
            before_dt = to_dt(before)
            results = [e for e in results if e.start is not None and e.start < before_dt]
        if after is not None:
            after_dt = to_dt(after)
            results = [e for e in results if e.start is not None and e.start > after_dt]

        return self.__class__(results)

    def sort_by_date(self, ascending: bool = True) -> EventCollection[E]:
        """Return a new EventCollection sorted by date, undated events last."""
        dated = sorted((e for e in self.data if e.start is not None), key=lambda e: e.start, reverse=not ascending)
        undated = [e for e in self.data if e.start is None]
        return self.__class__(dated + undated)

    def filter_by_competitors(self, competitor_ids: list[str]) -> EventCollection[MatchEvent]:
        """Return a new EventCollection containing only match events involving the specified competitor IDs."""
        wanted = set(competitor_ids)
        results = [
            event for event in self.matches
            if event.competitors
            and (event.competitors.home.id in wanted or event.competitors.away.id in wanted)
        ]
        return EventCollection(results)
