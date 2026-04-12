from enum import Enum


class SportContestNature(Enum):
    """
    Defines the nature of a sport, with two possible values:
    - OPPOSITION: A sport where competitors face off against each other (e.g. football, tennis).
    - COMPARISON: A sport where competitors are ranked based on performance metrics (e.g. motorsport, cycling).
    """
    OPPOSITION = "opposition"
    COMPARISON = "comparison"
