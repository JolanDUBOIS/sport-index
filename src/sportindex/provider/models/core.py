from .base import BaseSchema


class _SportData(BaseSchema):
    id: int
    name: str
    slug: str


class _CountryData(BaseSchema):
    name: str | None = None
    slug: str | None = None
    alpha2: str | None = None
    alpha3: str | None = None
    flag: str | None = None


class _CategoryData(BaseSchema):
    id: int
    name: str
    slug: str
    sport: _SportData
    alpha2: str | None = None
    flag: str | None = None
    country: _CountryData | None = None
