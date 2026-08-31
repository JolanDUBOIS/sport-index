"""Shared rendering for ``__repr__`` and ``__str__``.

One implementation backs every displayable type in the package — domain entities, the
provider schemas behind them, the small value models in between — so that output looks the
same wherever it comes from.

The two methods answer different questions. ``__repr__`` is for whoever is debugging: it
names the concrete class, quotes values, and lists the fields the type declares. ``__str__``
is for whoever is reading output: it collapses to the object's display name alone, so an
entity drops into a log line or an f-string without dragging its structure behind it.

Nested displayables never expand inside another object's repr. They collapse to a short
token naming their class and identity, which keeps a repr bounded however deep the object
graph runs.
"""

from __future__ import annotations

from typing import Any, ClassVar

#: Stands in for a field a type lists in its repr but the instance does not carry.
MISSING = "<missing>"

#: Fields a pydantic model prefers for its repr, when it declares none explicitly.
_PREFERRED_FIELDS = ("id", "name", "slug")

#: How many of a pydantic model's own fields to fall back on when none are preferred.
_DERIVED_FIELD_LIMIT = 3


def render_value(value: Any) -> str:
    """One field value, as it appears inside a repr.

    A nested displayable collapses to its token rather than its full repr; anything else is
    rendered by its own ``repr``.
    """
    if value is MISSING:
        return MISSING
    if isinstance(value, ReprMixin):
        return value._repr_token()
    return repr(value)


def render_repr(obj: Any, class_name: str, field_names: tuple[str, ...]) -> str:
    """The package's repr for ``obj``, listing ``field_names`` under ``class_name``."""
    fields = ", ".join(
        f"{name}={render_value(getattr(obj, name, MISSING))}" for name in field_names
    )
    return f"<{class_name} {fields}>" if fields else f"<{class_name}>"


class ReprMixin:
    """Gives a type the package's shared ``__repr__`` and ``__str__``.

    Attributes:
        _REPR_FIELDS: The field names ``__repr__`` lists, in order.
        _STR_FIELD: The attribute ``__str__`` returns. None — or an attribute the instance
            does not carry — falls back to ``__repr__``, which is what types with no obvious
            display name do.
    """

    _REPR_FIELDS: ClassVar[tuple[str, ...]] = ()
    _STR_FIELD: ClassVar[str | None] = "name"

    @classmethod
    def _repr_field_names(cls) -> tuple[str, ...]:
        """The fields ``__repr__`` lists, for types that declare them outright."""
        return cls._REPR_FIELDS

    def _repr_class_name(self) -> str:
        """The class name ``__repr__`` prints.

        The concrete class, deliberately: a repr is read while debugging, and a dispatch
        variant is exactly what one wants to see there. ``__str__`` is where the private
        name stays hidden.
        """
        return type(self).__name__

    def _repr_token(self) -> str:
        """How this object renders when it appears as a field of another object's repr."""
        identity = getattr(self, "id", None)
        if identity is None:
            return f"<{self._repr_class_name()}>"
        return f"<{self._repr_class_name()} {identity}>"

    def __repr__(self) -> str:
        return render_repr(self, self._repr_class_name(), self._repr_field_names())

    def __str__(self) -> str:
        if self._STR_FIELD is not None:
            display = getattr(self, self._STR_FIELD, None)
            if display is not None:
                return str(display)
        return repr(self)


class PydanticReprMixin(ReprMixin):
    """``ReprMixin`` for pydantic models, which derive their repr fields from their schema.

    A model with no explicit ``_REPR_FIELDS`` shows whichever of id, name and slug it
    actually declares, and falls back to its first few fields when it declares none of them.
    Deriving rather than declaring keeps a repr honest for the several dozen provider
    schemas, none of which would otherwise be worth listing fields for by hand.
    """

    @classmethod
    def _repr_field_names(cls) -> tuple[str, ...]:
        if cls._REPR_FIELDS:
            return cls._REPR_FIELDS

        model_fields: dict[str, Any] = getattr(cls, "model_fields", {})
        preferred = tuple(name for name in _PREFERRED_FIELDS if name in model_fields)
        if preferred:
            return preferred
        return tuple(model_fields)[:_DERIVED_FIELD_LIMIT]
