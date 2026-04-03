from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cached_property
from typing import (
    TYPE_CHECKING, Callable, Generic,
    TypeVar, Optional, Iterator,
    Iterable, Any, Union, overload
)

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

from sportindex.provider.models import BaseSchema
if TYPE_CHECKING:
    from .event import EventCollection
    from sportindex.provider import SofascoreProvider
    from sportindex.provider.models import _EventsResponse


T = TypeVar("T", bound=Union[BaseSchema, list[BaseSchema]])

class BaseEntity(ABC, Generic[T]):
    """Base class for all domain entities."""
    _data: T
    _REPR_FIELDS = ()

    def __init__(self, data: T, provider: SofascoreProvider, **kwargs) -> None:
        self._data = data
        self._provider = provider
        self._kwargs = kwargs

    @property
    def source(self) -> T:
        """Return the parsed data source for this entity."""
        return self._data

    def _clear_cache(self) -> None:
        for cls in type(self).mro():
            for attr_name, attr_value in vars(cls).items():
                if isinstance(attr_value, cached_property):
                    self.__dict__.pop(attr_name, None)

    def __repr__(self):
        field_str = ", ".join(f"{k}={getattr(self, k, '<missing>')!r}" for k in self._REPR_FIELDS)
        return f"<{self.__class__.__name__} {field_str}>"

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """
        Tells Pydantic how to validate this class when used as a field type.
        We simply tell it to enforce an `isinstance` check.
        """
        return core_schema.is_instance_schema(cls)


SingleT = TypeVar("SingleT", bound=BaseSchema)

class IdentifiableEntity(BaseEntity[SingleT]):
    """Base class for entities that have a unique identifier."""
    _ID_OFFSET_STEP = 10_000_000_000 # to avoid ID collisions across entity types when using several sofascore types for the same entity (e.g. competitions, seasons, events, competitors, etc.)

    @property
    @abstractmethod
    def id(self) -> int:
        """The unique ID of the entity, encoded as a globally unique SDK ID."""
        raise NotImplementedError("Subclasses of IdentifiableEntity must implement the id property")

    @classmethod
    def encode_id(cls, raw_id: int, type_idx: int) -> int:
        """Creates a globally unique SDK ID by combining the raw ID with a type index."""
        return (type_idx * cls._ID_OFFSET_STEP) + raw_id

    @classmethod
    def decode_id(cls, sdk_id: int) -> tuple[int, int]:
        """Splits an SDK ID back into its raw ID and type index components."""
        raw_id = sdk_id % cls._ID_OFFSET_STEP
        type_idx = sdk_id // cls._ID_OFFSET_STEP
        return raw_id, type_idx

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class EventAwareMixin:
    """
    Toolkit for entities that fetch fixtures and results.
    Provides shared pagination and unified date filtering.
    """

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Override in subclass if fixtures are supported."""
        raise NotImplementedError(f"Method get_fixtures must be implemented in the subclass {self.__class__.__name__}")

    def get_results(self, silent: bool = False) -> EventCollection:
        """Override in subclass if results are supported."""
        raise NotImplementedError(f"Method get_results must be implemented in the subclass {self.__class__.__name__}")

    def get_events(self) -> EventCollection:
        """Fetch all events."""
        events: EventCollection = self.get_results(silent=True) + self.get_fixtures(silent=True)
        return events.sort_by_date()

    def _fetch_paginated_events(self, provider_callable: Callable, *args, max_pages: int = 10) -> EventCollection:
        """Internal helper to exhaust a paginated provider endpoint."""
        from .event import Event, EventCollection
        parsed_events = []
        for page in range(max_pages):
            events_response: _EventsResponse = provider_callable(*args, page=page)
            parsed_events.extend(events_response.events)
            
            # Use getattr safely in case the response lacks hasNextPage
            if not getattr(events_response, "hasNextPage", False):
                break
                
        # self._provider exists because this mixin will be attached to BaseEntity subclasses
        return EventCollection([Event(e, getattr(self, "_provider")) for e in parsed_events])


E = TypeVar("E", bound=BaseEntity)

class EntityCollection(Generic[E]):
    """A generic collection of entities for any BaseEntity subclass."""

    def __init__(self, entities: Iterable[E] | None = None) -> None:
        self._entities = list(entities) if entities is not None else []

    def __iter__(self) -> Iterator[E]:
        return iter(self._entities)

    def __len__(self) -> int:
        return len(self._entities)

    def __add__(self, other: EntityCollection[E] | list[E]) -> EntityCollection[E]:
        if not isinstance(other, (EntityCollection, list)):
            return NotImplemented
        other_items = other._entities if isinstance(other, EntityCollection) else other
        return self.__class__(self._entities + other_items)

    def __iadd__(self, other: EntityCollection[E] | list[E]) -> EntityCollection[E]:
        if not isinstance(other, (EntityCollection, list)):
            return NotImplemented
        other_items = other._entities if isinstance(other, EntityCollection) else other
        self.extend(other_items)
        return self

    def __contains__(self, item: E) -> bool:
        return item in self._entities

    def append(self, entity: E) -> None:
        """Add a single entity to the collection."""
        self._entities.append(entity)

    def extend(self, collection: EntityCollection[E] | list[E]) -> None:
        """Add all entities from another collection."""
        items = collection._entities if isinstance(collection, EntityCollection) else collection
        self._entities.extend(items)

    @overload
    def __getitem__(self, key: int) -> E: ...

    @overload
    def __getitem__(self, key: slice) -> EntityCollection[E]: ...

    def __getitem__(self, key: int | slice) -> E | EntityCollection[E]:
        if isinstance(key, slice):
            return self.__class__(self._entities[key])
        return self._entities[key]

    def get(self, **kwargs) -> Optional[E]:
        """Get an entity by arbitrary attributes (e.g. id=1, name="Football")."""
        for e in self._entities:
            if all(getattr(e, k, None) == v for k, v in kwargs.items()):
                return e
        return None

    def search(self, query: str, by: str = "name") -> EntityCollection[E]:
        """
        Smart search that handles case-insensitivity, ignores extra spaces, 
        and allows for partial matches on a specified string attribute.
        Returns a new collection.
        """
        clean_query = query.strip().lower()
        results = [
            e for e in self._entities 
            if clean_query in str(getattr(e, by, "")).lower()
        ]
        return self.__class__(results)

    def to_list(self) -> list[E]:
        """Return the entities as a list."""
        return list(self._entities)

    def copy(self) -> EntityCollection[E]:
        """Return a shallow copy of the collection."""
        return self.__class__(self._entities.copy())

    def __or__(self, other: EntityCollection[E]) -> EntityCollection[E]:
        """Union (|): Returns a new collection with unique entities from both collections."""
        if not isinstance(other, EntityCollection):
            return NotImplemented
            
        if not self._entities and not other._entities:
            return self.__class__([])

        merged = list(dict.fromkeys(self._entities + other._entities))
        return self.__class__(merged)

    def __and__(self, other: EntityCollection[E]) -> EntityCollection[E]:
        """Intersection (&): Returns a new collection with entities common to both collections."""
        if not isinstance(other, EntityCollection):
            return NotImplemented
            
        if not self._entities or not other._entities:
            return self.__class__([])

        other_set = set(other._entities)
        common = list(dict.fromkeys(e for e in self._entities if e in other_set))
        return self.__class__(common)

    def __sub__(self, other: EntityCollection[E]) -> EntityCollection[E]:
        """Difference (-): Returns a new collection with entities in self but not in other."""
        if not isinstance(other, EntityCollection):
            return NotImplemented
            
        if not self._entities:
            return self.__class__([])
        if not other._entities:
            return self.copy()

        other_set = set(other._entities)
        diff = list(dict.fromkeys(e for e in self._entities if e not in other_set))
        return self.__class__(diff)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} count={len(self._entities)}>"

    def __str__(self) -> str:
        if not self._entities:
            return f"<{self.__class__.__name__} (empty)>"
        lines = [f"<{self.__class__.__name__} ({len(self._entities)} entities)>:"]
        for e in self._entities[:10]:  # Show up to 10 entities
            lines.append(f"  - {e!r}")
        if len(self._entities) > 10:
            lines.append(f"  ... and {len(self._entities) - 10} more")
        return "\n".join(lines)
