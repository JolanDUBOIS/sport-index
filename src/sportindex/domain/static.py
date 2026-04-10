"""
Static data — predefined sports and ranking-to-sport mappings.

These are known constants that don't change across API calls.
Sport objects are built lazily (on first access) so that this module
can be imported before ``BaseEntity.configure()`` has been called.
"""

from __future__ import annotations

from typing import Final, NamedTuple

from .enums import Gender


class SportEntry(NamedTuple):
    id: int
    slug: str
    name: str

SPORTS_REGISTRY: Final[tuple[SportEntry, ...]] = (
    SportEntry(1, "football", "Football"),
    SportEntry(2, "basketball", "Basketball"),
    SportEntry(4, "ice-hockey", "Ice Hockey"),
    SportEntry(5, "tennis", "Tennis"),
    SportEntry(6, "handball", "Handball"),
    SportEntry(11, "motorsport", "Motorsport"),
    SportEntry(12, "rugby", "Rugby"),
    SportEntry(15, "bandy", "Bandy"),
    SportEntry(19, "snooker", "Snooker"),
    SportEntry(20, "table-tennis", "Table Tennis"),
    SportEntry(22, "darts", "Darts"),
    SportEntry(23, "volleyball", "Volleyball"),
    SportEntry(26, "waterpolo", "Waterpolo"),
    SportEntry(29, "futsal", "Futsal"),
    SportEntry(31, "badminton", "Badminton"),
    SportEntry(34, "beach-volley", "Beach Volleyball"),
    SportEntry(62, "cricket", "Cricket"),
    SportEntry(63, "american-football", "American Football"),
    SportEntry(65, "cycling", "Cycling"),
    SportEntry(72, "esports", "Esports"),
    SportEntry(76, "mma", "MMA"),
    SportEntry(109, "minifootball", "Minifootball"),
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
