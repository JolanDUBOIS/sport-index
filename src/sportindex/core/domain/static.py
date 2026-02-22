"""
Static data — predefined sports and ranking-to-sport mappings.

These are known constants that don't change across API calls.
Sport objects are built lazily (on first access) so that this module
can be imported before ``BaseEntity.configure()`` has been called.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import Sport

# (id, slug, name) — raw tuples, no Sport instantiation at import time.
_SPORTS_DATA: tuple[tuple[int, str, str], ...] = (
    (1, "football", "Football"),
    (2, "basketball", "Basketball"),
    (4, "ice-hockey", "Ice Hockey"),
    (5, "tennis", "Tennis"),
    (6, "handball", "Handball"),
    (11, "motorsport", "Motorsport"),
    (12, "rugby", "Rugby"),
    (15, "bandy", "Bandy"),
    (19, "snooker", "Snooker"),
    (20, "table-tennis", "Table Tennis"),
    (22, "darts", "Darts"),
    (23, "volleyball", "Volleyball"),
    (26, "waterpolo", "Waterpolo"),
    (29, "futsal", "Futsal"),
    (31, "badminton", "Badminton"),
    (34, "beach-volley", "Beach Volleyball"),
    (62, "cricket", "Cricket"),
    (63, "american-football", "American Football"),
    (65, "cycling", "Cycling"),
    (72, "esports", "Esports"),
    (76, "mma", "MMA"),
    (109, "minifootball", "Minifootball"),
)

_sports_cache: list[Sport] | None = None


def get_sports() -> list[Sport]:
    """Return the list of known sports, building Sport objects on first call."""
    global _sports_cache
    if _sports_cache is None:
        from .core import Sport
        _sports_cache = [
            Sport(id=sid, slug=slug, name=name)
            for sid, slug, name in _SPORTS_DATA
        ]
    return _sports_cache

# Mapping: sport slug → list of (ranking_id, gender | None).
# gender is None when the ranking is not gender-specific.
SPORT_RANKINGS: dict[str, list[tuple[int, str | None]]] = {
    "football": [
        (1, "M"),          # UEFA Countries
        (2, "M"),          # FIFA Rankings
        (9, "M"),          # UEFA Clubs
    ],
    "tennis": [
        (5, "M"),        # ATP Rankings
        (6, "F"),      # WTA Rankings
        (7, "M"),        # ATP Rankings Live
        (8, "F"),      # WTA Rankings Live
        (34, "M"),       # UTR Men
        (35, "F"),     # UTR Women
    ],
    "rugby": [
        (3, "M"),          # Rugby Union Rankings
        (4, "M"),          # Rugby League Rankings
    ],
    "mma": [
        (11, "M"),       # UFC Flyweight
        (12, "M"),       # UFC Bantamweight
        (13, "M"),       # UFC Featherweight
        (14, "M"),       # UFC Lightweight
        (15, "M"),       # UFC Welterweight
        (16, "M"),       # UFC Middleweight
        (17, "M"),       # UFC Light Heavyweight
        (18, "M"),       # UFC Heavyweight
        (19, "F"),     # UFC Women's Strawweight
        (20, "F"),     # UFC Women's Flyweight
        (21, "F"),     # UFC Women's Bantamweight
        (22, "F"),     # UFC Women's Featherweight
    ],
}
