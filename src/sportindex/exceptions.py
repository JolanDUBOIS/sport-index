"""Package-level exceptions for sportindex.

Provide a small, stable hierarchy users can import from `sportindex.exceptions`.
"""

class SportIndexError(Exception):
    """Base class for all errors raised by sportindex."""


class ParseError(SportIndexError):
    """Raised when provider data cannot be parsed or mapped."""


class ProviderError(SportIndexError):
    """Base for errors coming from provider integration and network fetches."""


class NetworkError(ProviderError):
    """Network-level errors (connection, DNS, timeouts)."""


class RateLimitError(ProviderError):
    """Raised when an upstream service rate-limits requests (e.g. HTTP 429)."""


class ProviderNotFoundError(ProviderError):
    """Raised when a requested remote resource is not found (HTTP 404)."""


class FetchError(ProviderError):
    """Raised for general fetch failures (non-404/429 HTTP responses or exhausted retries)."""


class DomainError(SportIndexError):
    """Base class for domain/business-logic errors."""


class EntityNotFoundError(DomainError):
    """Raised when a requested domain entity cannot be found or constructed."""


class ConflictError(DomainError):
    """Raised when a business-logic conflict occurs (e.g. duplicate/unique constraint)."""


class InsufficientDataError(DomainError):
    """Raised when required data is missing or incomplete for domain operations."""


__all__ = [
    "SportIndexError",
    "ParseError",
    "ProviderError",
    "NetworkError",
    "RateLimitError",
    "ProviderNotFoundError",
    "FetchError",
    "DomainError",
    "EntityNotFoundError",
    "ConflictError",
    "InsufficientDataError",
]
