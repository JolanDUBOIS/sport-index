from __future__ import annotations

from abc import ABC
from typing import Generic, TypeVar, Optional

from . import logger
from sportindex.core.provider.parsed import ParsedSofascoreProvider, BaseParsedModel


_default_provider = None

def _get_default_provider() -> ParsedSofascoreProvider:
    global _default_provider
    if _default_provider is None:
        _default_provider = ParsedSofascoreProvider()
    return _default_provider

T = TypeVar("T", bound=BaseParsedModel)

class BaseEntity(ABC, Generic[T]):
    """Base class for all domain entities."""
    _data: T | list[T]
    REPR_FIELDS = ("id",)

    def __init__(self, data: T | list[T], provider: ParsedSofascoreProvider | None = None, **kwargs) -> None:
        self._data = data
        self._provider = provider or _get_default_provider()
        self._kwargs = kwargs

    @property
    def id(self) -> Optional[int]:
        """The unique ID of this entity."""
        if isinstance(self._data, list):
            logger.warning(f"Entity {self.__class__.__name__} has a list of data, cannot determine ID")
            return None

        try:
            return self._data.id
        except AttributeError:
            logger.warning(f"Entity {self.__class__.__name__} has no 'id' attribute in its data")
            return None

    @property
    def details(self) -> T | list[T]:
        """Return the raw data used to create this entity."""
        return self._data

    def __repr__(self):
        field_str = ", ".join(f"{k}={getattr(self, k)!r}" for k in self.REPR_FIELDS)
        return f"<{self.__class__.__name__} {field_str}>"
