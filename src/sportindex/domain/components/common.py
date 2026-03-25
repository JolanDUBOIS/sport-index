from __future__ import annotations

from enum import Enum
from dataclasses import dataclass

from . import logger
from sportindex.provider.parsed import ParsedAmount, ParsedPromotion, ParsedPerformance


class Gender(str, Enum):
    """Standardized representation of gender for competitors.

    Values:
        UNSPECIFIED ("X"): Unknown or not specified.
        MALE ("M"): Male.
        FEMALE ("F"): Female.
    """
    UNSPECIFIED = "X"
    MALE = "M"
    FEMALE = "F"

    @classmethod
    def _missing_(cls, value):
        # This triggers if 'value' is not "X", "M", or "F".
        logger.debug(f"Received unknown gender value '{value}', defaulting to UNSPECIFIED")
        return cls.UNSPECIFIED


@dataclass(frozen=True)
class Amount:
    """Represents a monetary amount, such as transfer fees or prize money."""
    __annotations__ = ParsedAmount.__annotations__

    @classmethod
    def _from_parsed(cls, parsed: ParsedAmount | None, **kwargs) -> Amount | None:
        if parsed is None:
            return None
        return cls(**vars(parsed))


@dataclass(frozen=True)
class Promotion:
    """Represents promotion/relegation status in a standings entry."""
    __annotations__ = ParsedPromotion.__annotations__

    @classmethod
    def _from_parsed(cls, parsed: ParsedPromotion | None, **kwargs) -> Promotion | None:
        if parsed is None:
            return None
        return cls(**vars(parsed))


@dataclass(frozen=True)
class Performance:
    """Represents performance statistics for a team or manager."""
    __annotations__ = ParsedPerformance.__annotations__

    @classmethod
    def _from_parsed(cls, parsed: ParsedPerformance | None, **kwargs) -> Performance | None:
        if parsed is None:
            return None
        return cls(**vars(parsed))
