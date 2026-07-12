from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from functools import cached_property
from typing import TYPE_CHECKING, Any, Self

from pydantic_core import core_schema

from sportindex.exceptions import ProviderNotFoundError

from .utils import merge_pydantic_models

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

    @property
    def _public_class_name(self) -> str:
        for cls in self.__class__.__mro__:
            if not cls.__name__.startswith("_"):
                return cls.__name__
        return self.__class__.__name__

    def __str__(self) -> str:
        field_str = ", ".join(f"{k}={getattr(self, k, '<missing>')}" for k in self._REPR_FIELDS)
        return f"<{self._public_class_name} {field_str}>"

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
    _PREFIX: str

    def __init__(self, data: BaseSchema, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)
        self._full_loaded = False

    @property
    @abstractmethod
    def id(self) -> str:
        """The unique ID of the entity, encoded as a globally unique SDK ID."""
        raise NotImplementedError("Subclasses of IdentifiableEntity must implement the id property")

    @classmethod
    def encode_id(cls, raw_id: int, parent_id: str | None = None) -> str:
        """Encodes the raw provider ID into a single unique SDK ID."""
        base_id = f"{cls._PREFIX}:{raw_id}"
        return f"{parent_id}:{base_id}" if parent_id else base_id

    @classmethod
    def decode_id(cls, sdk_id: str) -> tuple[str | None, str, int]:
        """Decodes the combined SDK ID into (parent_id, prefix, raw_id).

        Splits from the right so a `parent_id` that is itself a compound ID
        (e.g. a Competition ID nested inside a Season ID) is kept intact
        instead of being shredded by a naive left-to-right split.
        """
        parts = sdk_id.rsplit(":", 2)
        if len(parts) == 2:
            prefix, raw_id = parts
            return None, prefix, int(raw_id)
        if len(parts) == 3:
            parent_id, prefix, raw_id = parts
            return parent_id, prefix, int(raw_id)
        raise ValueError(f"Invalid SDK ID format: {sdk_id}")

    @classmethod
    def _get_all_subclasses(cls, base_cls: type[Any]) -> set[type[Any]]:
        subclasses = set()
        for sub in base_cls.__subclasses__():
            subclasses.add(sub)
            subclasses.update(cls._get_all_subclasses(sub))
        return subclasses

    @classmethod
    def _process_parent_id(cls, parent_id: str | None, provider: SofascoreProvider) -> dict[str, Any]:
        return {}

    @classmethod
    def from_id(cls, entity_id: str, provider: SofascoreProvider) -> Self:
        parent_id, prefix, raw_id = cls.decode_id(entity_id)
        logger.debug(f"Decoded ID '{entity_id}' into parent_id='{parent_id}', prefix='{prefix}', raw_id={raw_id}")
        target_class = None

        if getattr(cls, "_PREFIX", None) == prefix:
            target_class = cls
        else:
            for sub in cls._get_all_subclasses(cls):
                if getattr(sub, "_PREFIX", None) == prefix:
                    target_class = sub
                    break

        if target_class is None:
            for sub in cls._get_all_subclasses(IdentifiableEntity):
                if getattr(sub, "_PREFIX", None) == prefix:
                    raise ValueError(
                        f"Prefix '{prefix}' matches {sub.__name__}, "
                        f"which is not a subclass of {cls.__name__}."
                    )
            raise ValueError(f"No subclass found globally with prefix '{prefix}'.")

        extra_kwargs = target_class._process_parent_id(parent_id, provider)
        data = target_class._fetch_entity(raw_id, provider, **extra_kwargs)
        return target_class(data, provider, **extra_kwargs)

    def _full_load(self) -> None:
        """
        Lazy-loads the complete entity from the provider.
        Called automatically when accessing properties that require full details
        missing from the initial lightweight API response.
        """
        if self._full_loaded:
            return
        self._data = merge_pydantic_models(self._data, self._fetch_entity(self.decode_id(self.id)[2], self._provider))
        self._full_loaded = True
        self._clear_cache()

    @staticmethod
    @abstractmethod
    def _fetch_entity(raw_id: int, provider: SofascoreProvider, **kwargs) -> BaseSchema: # TODO - It actually returns the specific BaseSchema of _data...
        """Fetch the complete entity data from the provider by its raw ID."""
        raise NotImplementedError("Subclasses of IdentifiableEntity must implement the _fetch_entity static method")

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
                    try:
                        scored_items.append((cls(item.entity, provider), item.score))
                    except (ValueError, TypeError) as e:
                        logger.debug(f"Skipping search result incompatible with {cls.__name__}: {e}")

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
