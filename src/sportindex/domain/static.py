"""
Static data — predefined sports and ranking-to-sport mappings.

These are known constants that don't change across API calls.
Sport objects are built lazily (on first access) so that this module
can be imported before ``BaseEntity.configure()`` has been called.
"""

from __future__ import annotations

from typing import Final, NamedTuple

from .enums import Gender
from .types import EventFormat


class SportEntry(NamedTuple):
    id: int
    slug: str
    name: str
    event_format: EventFormat

SPORTS_REGISTRY: Final[tuple[SportEntry, ...]] = (
    SportEntry(1, "football", "Football", "match"),
    SportEntry(2, "basketball", "Basketball", "match"),
    SportEntry(4, "ice-hockey", "Ice Hockey", "match"),
    SportEntry(5, "tennis", "Tennis", "match"),
    SportEntry(6, "handball", "Handball", "match"),
    SportEntry(11, "motorsport", "Motorsport", "stage"),
    SportEntry(12, "rugby", "Rugby", "match"),
    SportEntry(15, "bandy", "Bandy", "match"),
    SportEntry(19, "snooker", "Snooker", "match"),
    SportEntry(20, "table-tennis", "Table Tennis", "match"),
    SportEntry(22, "darts", "Darts", "match"),
    SportEntry(23, "volleyball", "Volleyball", "match"),
    SportEntry(26, "waterpolo", "Waterpolo", "match"),
    SportEntry(29, "futsal", "Futsal", "match"),
    SportEntry(31, "badminton", "Badminton", "match"),
    SportEntry(34, "beach-volley", "Beach Volleyball", "match"),
    SportEntry(62, "cricket", "Cricket", "match"),
    SportEntry(63, "american-football", "American Football", "match"),
    SportEntry(65, "cycling", "Cycling", "stage"),
    SportEntry(72, "esports", "Esports", "match"),
    SportEntry(76, "mma", "MMA", "match"),
    SportEntry(109, "minifootball", "Minifootball", "match"),
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
