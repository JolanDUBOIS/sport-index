from __future__ import annotations
from typing import TypedDict


class Sport(TypedDict, total=False):
    id: int
    name: str
    slug: str


class Country(TypedDict, total=False):
    name: str
    slug: str
    alpha2: str
    alpha3: str
    flag: str


class Category(TypedDict, total=False):
    id: int
    name: str
    slug: str
    sport: Sport
    alpha2: str
    flag: str
    country: Country
