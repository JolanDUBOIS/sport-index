from __future__ import annotations

from typing import Iterator, Any, get_origin, get_args, get_type_hints

from . import logger


# =====================================================================
# Core base model
# =====================================================================

class BaseModel:
    """
    Base class for lightweight typed raw models.

    Features:
    - Missing annotated fields default to None.
    - Unknown fields are preserved.
    - Nested BaseModel, list[BaseModel], dict[str, BaseModel] supported.
    - Best-effort type coercion with warning on failure.
    """

    # ---------------------------
    # Construction
    # ---------------------------

    def __init__(self, **data: Any) -> None:
        annotations = get_type_hints(self.__class__)
        self._extra: dict[str, Any] = {}

        # Handle annotated fields
        for field_name, field_type in annotations.items():
            if field_name in data:
                value = data[field_name]
                coerced = self._coerce(field_type, value, field_name)
                setattr(self, field_name, coerced)
            else:
                setattr(self, field_name, None)

        # Preserve extra fields
        for key, value in data.items():
            if key not in annotations:
                self._extra[key] = value

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseModel:
        """Convenience method to construct from a dict."""
        return cls(**data)

    # ---------------------------
    # Type coercion
    # ---------------------------

    @classmethod
    def _coerce(cls, expected_type: Any, value: Any, field_name: str) -> Any:
        if value is None:
            return None

        origin = get_origin(expected_type)
        args = get_args(expected_type)

        # Nested BaseModel
        if isinstance(expected_type, type) and issubclass(expected_type, BaseModel):
            if isinstance(value, dict):
                return expected_type.from_dict(value)
            return value

        # list[T]
        if origin is list and args:
            inner = args[0]
            if isinstance(value, list):
                return [cls._coerce(inner, v, field_name) for v in value]
            return value

        # dict[K, V]
        if origin is dict and len(args) == 2:
            key_type, val_type = args
            if isinstance(value, dict):
                return {
                    cls._coerce(key_type, k, field_name):
                    cls._coerce(val_type, v, field_name)
                    for k, v in value.items()
                }
            return value

        # Primitive coercion
        try:
            if not isinstance(value, expected_type):
                return expected_type(value)
            return value
        except Exception:
            logger.warning(
                "Failed to coerce field '%s': %r to %r",
                field_name,
                value,
                expected_type,
            )
            return value

    # ---------------------------
    # Field access and extras
    # ---------------------------

    def __getattr__(self, item: str) -> Any:
        if "_extra" in self.__dict__ and item in self._extra:
            return self._extra[item]
        raise AttributeError(item)

    def __getitem__(self, item: str) -> Any:
        """Allows dictionary-style access: value = model['field']"""
        annotations = get_type_hints(self.__class__)
        if item in annotations:
            return getattr(self, item)
        if hasattr(self, "_extra") and item in self._extra:
            return self._extra[item]
        raise KeyError(item)

    def __iter__(self) -> Iterator[str]:
        """Allows iterating over keys: for key in model: ..."""
        annotations = get_type_hints(self.__class__)
        for field in annotations:
            yield field
        if hasattr(self, "_extra"):
            for key in self._extra:
                yield key

    def __contains__(self, key: str) -> bool:
        """Check if a field (annotated or extra) exists."""
        annotations = get_type_hints(self.__class__)
        return key in annotations or key in self._extra

    def get(self, key: str, default: Any = None) -> Any:
        """Dictionary-style get method."""
        try:
            return self[key]
        except KeyError:
            return default

    # ---------------------------
    # Serialization
    # ---------------------------

    def to_dict(self, strip: bool = False) -> dict[str, Any]:
        """Convert to dict, optionally stripping unknown fields (strip=True)."""
        annotations = get_type_hints(self.__class__)
        result: dict[str, Any] = {
            field_name: self._serialize(getattr(self, field_name), strip=strip)
            for field_name in annotations
        }
        
        if strip:
            # Only annotated fields, no extras
            return result

        # Default: include extra fields
        result.update(self._extra)
        return result

    @classmethod
    def _serialize(cls, value: Any, strip: bool = False) -> Any:
        if isinstance(value, BaseModel):
            return value.to_dict(strip=strip)
        if isinstance(value, list):
            return [cls._serialize(v, strip=strip) for v in value]
        if isinstance(value, dict):
            return {k: cls._serialize(v, strip=strip) for k, v in value.items()}
        return value

    # ---------------------------
    # Representation
    # ---------------------------

    def __repr__(self) -> str:
        annotations = get_type_hints(self.__class__)
        fields = {field: getattr(self, field) for field in annotations}
        return f"{self.__class__.__name__}({fields}, extra={self._extra})"

    # ---------------------------
    # Copying and immutability
    # ---------------------------

    def copy(self, **overrides: Any) -> BaseModel:
        """Create a copy of this model, optionally overriding some fields."""
        data = self.to_dict(strip=False)
        data.update(overrides)
        return self.__class__(**data)
