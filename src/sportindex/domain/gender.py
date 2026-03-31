from __future__ import annotations

from enum import Enum

from . import logger


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
