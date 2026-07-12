from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

BASE_URL_LEN = len("https://www.sofascore.com/")


@dataclass(slots=True)
class _SitemapStub(ABC):
    id: int
    slug: str

    @classmethod
    @abstractmethod
    def from_url(cls, url: str) -> _SitemapStub:
        raise NotImplementedError

    @classmethod
    def from_url_batch(cls, urls: list[str]) -> list[_SitemapStub]:
        return [cls.from_url(u) for u in urls]


@dataclass(slots=True)
class _ManagerStub(_SitemapStub):
    sport_slug: str

    @classmethod
    def from_url(cls, url: str) -> _ManagerStub:
        parts = url[BASE_URL_LEN:].split("/", 4)
        return cls(
            id=int(parts[3]),
            slug=parts[2],
            sport_slug=parts[0],
        )


@dataclass(slots=True)
class _PlayerStub(_SitemapStub):
    sport_slug: str

    @classmethod
    def from_url(cls, url: str) -> _PlayerStub:
        parts = url[BASE_URL_LEN:].split("/", 4)
        return cls(
            id=int(parts[3]),
            slug=parts[2],
            sport_slug=parts[0],
        )


@dataclass(slots=True)
class _RaceStub(_SitemapStub):
    sport_slug: str

    @classmethod
    def from_url(cls, url: str) -> _RaceStub:
        parts = url[BASE_URL_LEN:].split("/", 4)
        return cls(
            id=int(parts[3]),
            slug=parts[2],
            sport_slug=parts[0],
        )


@dataclass(slots=True)
class _TeamStub(_SitemapStub):
    sport_slug: str

    @classmethod
    def from_url(cls, url: str) -> _TeamStub:
        parts = url[BASE_URL_LEN:].split("/", 4)
        return cls(
            id=int(parts[3]),
            slug=parts[2],
            sport_slug=parts[0],
        )


@dataclass(slots=True)
class _TournamentStub(_SitemapStub):
    sport_slug: str
    category_slug: str

    @classmethod
    def from_url(cls, url: str) -> _TournamentStub:
        parts = url[BASE_URL_LEN:].split("/", 5)
        return cls(
            id=int(parts[4]),
            slug=parts[3],
            sport_slug=parts[0],
            category_slug=parts[2],
        )


@dataclass(slots=True)
class _VenueStub(_SitemapStub):
    country_slug: str

    @classmethod
    def from_url(cls, url: str) -> _VenueStub:
        parts = url[BASE_URL_LEN:].split("/", 4)
        return cls(
            id=int(parts[3]),
            slug=parts[2],
            country_slug=parts[1],
        )
