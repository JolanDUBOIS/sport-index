from typing import Callable, Any, TypeVar

F = TypeVar('F', bound=Callable[..., Any])

PARSERS: dict[type, Callable[[Any], Any]] = {}

def register(type_: type):
    """Decorator to register a parser function for a specific model type."""
    def decorator(fn: F) -> F:
        if type_ in PARSERS:
            raise ValueError(f"Parser already registered for type {type_!r}")
        PARSERS[type_] = fn
        return fn
    return decorator

def get_parser(type_: type) -> Callable[[Any], Any] | None:
    """Fetch the parser for a specific type, or None if not registered."""
    return PARSERS.get(type_)
