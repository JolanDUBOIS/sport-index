from __future__ import annotations
from typing import TypeVar, Dict, Any

from dataclasses import dataclass, fields


T = TypeVar("T", bound="BaseParsedModel")

@dataclass
class BaseParsedModel:
    """
    Base dataclass for all parsed models. 
    Provides a common interface for parsing raw data into structured dataclasses.
    """

    @classmethod
    def from_raw(cls: type[T], raw: Dict | None, *args: Any, **kwargs: Any) -> T | None:
        """
        Public entry point. Safely returns None if the raw input is None.
        Also filters out any unexpected keys from the raw data before parsing.
        Otherwise, delegates to the internal _parse method which must be implemented by subclasses.
        """
        if not raw:
            return None
        return cls._parse(raw, *args, **kwargs)

    @classmethod
    def _parse(cls: type[T], raw: Any, *args: Any, **kwargs: Any) -> T:
        """
        Default parsing logic. If a subclass doesn't override this, 
        it safely auto-maps the dictionary by ignoring extra keys.
        """
        return cls._auto_map(raw)

    @classmethod
    def _auto_map(cls: type[T], raw: Dict[str, Any]) -> T:
        """
        Helper to unpack a dict, ignoring extra fields 
        and defaulting missing fields to None.
        """
        clean_raw = {
            f.name: raw.get(f.name, None) 
            for f in fields(cls)
        }
        return cls(**clean_raw)
