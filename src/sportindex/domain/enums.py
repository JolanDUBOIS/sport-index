from __future__ import annotations

import logging
from enum import StrEnum

logger = logging.getLogger(__name__)


class Gender(StrEnum):
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
