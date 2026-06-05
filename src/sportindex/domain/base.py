from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from functools import cached_property
from typing import TYPE_CHECKING, Any, Self

from pydantic_core import core_schema

from sportindex.exceptions import ProviderNotFoundError

if TYPE_CHECKING:
    from collections.abc import Callable

    from pydantic import GetCoreSchemaHandler

    from sportindex.api_client import SofascoreProvider
    from sportindex.api_client.models import BaseSchema, _SearchResultData

    from .collections import ScoredEntityCollection

logger = logging.getLogger(__name__)


# ===== Base Entity =====

class BaseEntity(ABC):
    """Base class for all domain entities."""
    _data: BaseSchema
    _REPR_FIELDS = ()

    def __init__(self, data: BaseSchema, provider: SofascoreProvider, **kwargs) -> None:
        self._data = data
        self._provider = provider
        self._kwargs = kwargs

    @property
    def source(self) -> BaseSchema:
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

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """
        Tells Pydantic how to validate this class when used as a field type.
        We simply tell it to enforce an `isinstance` check.
        """
        return core_schema.is_instance_schema(cls)


# ===== Identifiable Entity =====

class IdentifiableEntity(BaseEntity):
    """Base class for entities that have a unique identifier."""
    _N_TYPES: int = 1

    @property
    @abstractmethod
    def id(self) -> int:
        """The unique ID of the entity, encoded as a globally unique SDK ID."""
        raise NotImplementedError("Subclasses of IdentifiableEntity must implement the id property")

    @classmethod
    def encode_id(cls, raw_id: int, type_idx: int) -> int:
        """Encodes the raw provider ID and type index into a single unique SDK ID."""
        if type_idx > cls._N_TYPES or type_idx < 1:
            raise ValueError(f"type_idx {type_idx} exceeds maximum _N_TYPES ({cls._N_TYPES}) for {cls.__name__}")
        return (raw_id * cls._N_TYPES) + (type_idx - 1)

    @classmethod
    def decode_id(cls, sdk_id: int) -> tuple[int, int]:
        """Decodes the combined SDK ID into (raw_id, type_idx)."""
        raw_id = sdk_id // cls._N_TYPES
        type_idx = (sdk_id % cls._N_TYPES) + 1
        return raw_id, type_idx

    @classmethod
    @abstractmethod
    def from_id(cls, entity_id: int, provider: SofascoreProvider) -> Self:
        """Create an instance of the entity from its unique ID."""
        raise NotImplementedError("Subclasses of IdentifiableEntity must implement the from_id class method")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash((type(self), self.id))


# ===== Searchable Mixin =====

class SearchableMixin(IdentifiableEntity):
    """
    Mixin for entities that can be searched via pagination.

    Methods:
        search() -> ScoredEntityCollection[Self]: Search for entities matching a query, with pagination support.
    """

    @classmethod
    def _paginate_search(
        cls,
        query: str,
        provider: SofascoreProvider,
        search_func: Callable[[str, int], list[_SearchResultData]],
        valid_types: tuple[type, ...] | None = None,
        max_results: int = 20,
        max_pages: int = 50,
    ) -> ScoredEntityCollection[Self]:
        """Helper method to perform paginated search and collect scored results."""
        scored_items = []
        for page in range(max_pages + 1):
            try:
                matches = search_func(query, page)
            except ProviderNotFoundError as e:
                logger.debug(f"Search for query '{query}' not found on page {page}: {e}")
                break

            if not matches:
                break

            for item in matches:
                if valid_types is None or isinstance(item.entity, valid_types):
                    scored_items.append((cls(item.entity, provider), item.score))

                if len(scored_items) >= max_results:
                    break

            if len(scored_items) >= max_results:
                break

        from .collections import ScoredEntityCollection
        return ScoredEntityCollection(scored_items[:max_results])

    @staticmethod
    def _validate_query(query: str) -> None:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Search query must be a non-empty string")

    @classmethod
    @abstractmethod
    def search(cls, query: str, provider: SofascoreProvider, max_results: int = 20) -> ScoredEntityCollection[Self]:
        """Search for entities matching the query using the provider's search functionality."""
        raise NotImplementedError("Subclasses of SearchableMixin must implement the search class method")
