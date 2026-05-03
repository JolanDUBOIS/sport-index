"""
Static data — predefined sports and ranking-to-sport mappings.

These are known constants that don't change across API calls.
Sport objects are built lazily (on first access) so that this module
can be imported before ``BaseEntity.configure()`` has been called.
"""

from __future__ import annotations

from typing import Final, NamedTuple

from ..types import SportContestNature
from .enums import Gender


class SportEntry(NamedTuple):
    id: int
    slug: str
    name: str
    nature: SportContestNature

SPORTS_REGISTRY: Final[tuple[SportEntry, ...]] = (
    SportEntry(1, "football", "Football", SportContestNature.OPPOSITION),
    SportEntry(2, "basketball", "Basketball", SportContestNature.OPPOSITION),
    SportEntry(4, "ice-hockey", "Ice Hockey", SportContestNature.OPPOSITION),
    SportEntry(5, "tennis", "Tennis", SportContestNature.OPPOSITION),
    SportEntry(6, "handball", "Handball", SportContestNature.OPPOSITION),
    SportEntry(11, "motorsport", "Motorsport", SportContestNature.COMPARISON),
    SportEntry(12, "rugby", "Rugby", SportContestNature.OPPOSITION),
    SportEntry(15, "bandy", "Bandy", SportContestNature.OPPOSITION),
    SportEntry(19, "snooker", "Snooker", SportContestNature.OPPOSITION),
    SportEntry(20, "table-tennis", "Table Tennis", SportContestNature.OPPOSITION),
    SportEntry(22, "darts", "Darts", SportContestNature.OPPOSITION),
    SportEntry(23, "volleyball", "Volleyball", SportContestNature.OPPOSITION),
    SportEntry(26, "waterpolo", "Waterpolo", SportContestNature.OPPOSITION),
    SportEntry(29, "futsal", "Futsal", SportContestNature.OPPOSITION),
    SportEntry(31, "badminton", "Badminton", SportContestNature.OPPOSITION),
    SportEntry(34, "beach-volley", "Beach Volleyball", SportContestNature.OPPOSITION),
    SportEntry(62, "cricket", "Cricket", SportContestNature.OPPOSITION),
    SportEntry(63, "american-football", "American Football", SportContestNature.OPPOSITION),
    SportEntry(65, "cycling", "Cycling", SportContestNature.COMPARISON),
    SportEntry(72, "esports", "Esports", SportContestNature.OPPOSITION),
    SportEntry(76, "mma", "MMA", SportContestNature.OPPOSITION),
    SportEntry(109, "minifootball", "Minifootball", SportContestNature.OPPOSITION),
)

# Mapping: sport slug → list of (ranking_id, gender | None)
SPORT_RANKINGS: dict[str, list[tuple[int, Gender]]] = {
    "football": [
        (1, Gender.MALE),        # UEFA Countries
        (2, Gender.MALE),        # FIFA Rankings
        (9, Gender.MALE),        # UEFA Clubs
    ],
    "tennis": [
        (5, Gender.MALE),        # ATP Rankings
        (6, Gender.FEMALE),      # WTA Rankings
        (7, Gender.MALE),        # ATP Rankings Live
        (8, Gender.FEMALE),      # WTA Rankings Live
        (34, Gender.MALE),       # UTR Men
        (35, Gender.FEMALE),     # UTR Women
    ],
    "rugby": [
        (3, Gender.MALE),        # Rugby Union Rankings
        (4, Gender.MALE),        # Rugby League Rankings
    ],
    "mma": [
        (11, Gender.MALE),       # UFC Flyweight
        (12, Gender.MALE),       # UFC Bantamweight
        (13, Gender.MALE),       # UFC Featherweight
        (14, Gender.MALE),       # UFC Lightweight
        (15, Gender.MALE),       # UFC Welterweight
        (16, Gender.MALE),       # UFC Middleweight
        (17, Gender.MALE),       # UFC Light Heavyweight
        (18, Gender.MALE),       # UFC Heavyweight
        (19, Gender.FEMALE),     # UFC Women's Strawweight
        (20, Gender.FEMALE),     # UFC Women's Flyweight
        (21, Gender.FEMALE),     # UFC Women's Bantamweight
        (22, Gender.FEMALE),     # UFC Women's Featherweight
    ],
}
