from __future__ import annotations
from typing import TypeVar, Dict, Any

T = TypeVar("T", bound="BaseParsedModel")

class BaseParsedModel:
    @classmethod
    def from_raw(cls: type[T], raw: Dict | None, *args: Any, **kwargs: Any) -> T | None:
        """
        Public entry point. 
        Safely returns None if the raw input is None.
        Otherwise, passes arguments to the subclass's _parse method.
        """
        if raw is None:
            return None
        return cls._parse(raw, *args, **kwargs)

    @classmethod
    def _parse(cls: type[T], raw: Any, *args: Any, **kwargs: Any) -> T:
        """
        Internal parsing logic to be overridden by child classes.
        """
        raise NotImplementedError("Subclasses must implement _parse")
