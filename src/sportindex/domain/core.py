from __future__ import annotations

from enum import Enum
from functools import cached_property
from typing import TYPE_CHECKING, Optional

import pycountry

from . import logger
from .base import BaseEntity, IdentifiableEntity, EntityCollection
from .static import SPORT_RANKINGS
from sportindex.exceptions import ProviderNotFoundError
from sportindex.provider.parsed import (
    ParsedSport,
    ParsedCountry,
    ParsedCategory
)

if TYPE_CHECKING:
    from .leaderboard import Rankings
    from .competition import Competition
    from sportindex.provider.parsed import ParsedSofascoreProvider


class Sport(IdentifiableEntity[ParsedSport]):
    """A sport, e.g. football, tennis, motorsport, etc."""
    REPR_FIELDS = ("id", "name", "slug")

    def __init__(self, data: ParsedSport, provider: ParsedSofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, ParsedSport):
            raise TypeError("Sport data must be of type ParsedSport")

    @property
    def id(self) -> int:
        """The unique ID of the sport."""
        return self._data.id

    @property
    def name(self) -> str:
        """The name of the sport."""
        return self._data.name

    @property
    def slug(self) -> str:
        """The slug of the sport (used in URLs)."""
        return self._data.slug or self._data.name.lower().replace(" ", "-")

    @cached_property
    def categories(self) -> EntityCollection[Category]:
        """Fetch all categories for this sport."""
        return EntityCollection([
            Category(c, self._provider)
            for c in self._provider.get_categories(self.slug)
        ])

    def get_rankings(self, gender: Optional[str] = None) -> list[Rankings]:
        """Fetch all rankings for this sport."""
        from .leaderboard import Rankings
        rankings = []
        for ranking_id, ranking_gender in SPORT_RANKINGS.get(self.slug, []):
            if gender is None or ranking_gender == gender:
                rankings.append(Rankings(
                    self._provider.get_ranking(ranking_id),
                    provider=self._provider,
                ))
        return rankings

    @classmethod
    def _from_tuple(cls, data: tuple[int, str, str], provider: ParsedSofascoreProvider) -> Sport:
        """Create a Sport instance from a raw tuple (id, slug, name). This is used to build the initial list of sports without needing to fetch categories or rankings."""
        sid, slug, name = data
        return cls(ParsedSport(id=sid, slug=slug, name=name), provider)

    # Events ? 


class Country(BaseEntity[ParsedCountry]):
    """ A country, e.g. France, England, Spain, etc."""
    REPR_FIELDS = ("name", "slug", "alpha2", "alpha3")

    def __init__(self, data: ParsedCountry, provider: ParsedSofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, ParsedCountry):
            raise TypeError("Country data must be of type ParsedCountry")

        self._country = next(
            (c for c in pycountry.countries if c.name.lower() == self.name.lower()), None
        )

    @property
    def name(self) -> str:
        """The name of the country."""
        return self._data.name.title() or self._data.slug.replace("-", " ").title()

    @property
    def slug(self) -> str:
        """The slug of the country (used in URLs)."""
        return self._data.slug

    @property
    def alpha2(self) -> Optional[str]:
        """The alpha-2 code of the country (e.g. 'FR' for France)."""
        return self._data.alpha2 or (self._country.alpha_2 if self._country else None)

    @property
    def alpha3(self) -> Optional[str]:
        """The alpha-3 code of the country (e.g. 'FRA' for France)."""
        return self._data.alpha3 or (self._country.alpha_3 if self._country else None)

    @classmethod
    def from_alpha(cls, alpha: str, provider: ParsedSofascoreProvider) -> Optional[Country]:
        """Create a Country instance from an alpha-2 or alpha-3 code."""
        country = next(
            (c for c in pycountry.countries if c.alpha_2 == alpha.upper() or c.alpha_3 == alpha.upper()), None
        )
        if country:
            return cls(
                data=ParsedCountry(
                    name=country.name,
                    slug=country.name.lower().replace(" ", "-"),
                    alpha2=country.alpha_2,
                    alpha3=country.alpha_3
                ),
                provider=provider
            )
        return None

    @classmethod
    def from_name(cls, name: str, provider: ParsedSofascoreProvider) -> Optional[Country]:
        """Create a Country instance from a country name."""
        country = next(
            (c for c in pycountry.countries if c.name.lower() == name.lower()), None
        )
        if country:
            return cls(
                data=ParsedCountry(
                    name=country.name,
                    slug=country.name.lower().replace(" ", "-"),
                    alpha2=country.alpha_2,
                    alpha3=country.alpha_3
                ),
                provider=provider
            )
        return None


class Category(IdentifiableEntity[ParsedCategory]):
    """A category within a sport (e.g. 'France Amateur', 'Formula 1', 'International')."""
    REPR_FIELDS = ("id", "name", "slug", "sport", "country")

    def __init__(self, data: ParsedCategory, provider: ParsedSofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, ParsedCategory):
            raise TypeError("Category data must be of type ParsedCategory")

    @property
    def id(self) -> int:
        """The unique ID of the category."""
        return self._data.id

    @property
    def name(self) -> str:
        """The name of the category."""
        return self._data.name

    @property
    def slug(self) -> str:
        """The slug of the category (used in URLs)."""
        return self._data.slug or self._data.name.lower().replace(" ", "-")

    @cached_property
    def sport(self) -> Sport:
        """The sport this category belongs to."""
        return Sport(self._data.sport, self._provider)

    @cached_property
    def country(self) -> Optional[Country]:
        """The country this category belongs to, or None if it's an international category."""
        if self._data.country:
            return Country(self._data.country, self._provider)
        return None

    @cached_property
    def competitions(self) -> EntityCollection[Competition]:
        """Fetch all competitions (unique tournaments / unique stages) for this category."""
        try:
            unique_tournaments = self._provider.get_category_unique_tournaments(self.id)
        except ProviderNotFoundError:
            unique_tournaments = []
        try:
            unique_stages = self._provider.get_category_unique_stages(self.id)
        except ProviderNotFoundError:
            unique_stages = []

        from .competition import Competition
        return EntityCollection([
            Competition(c, self._provider) for c in unique_tournaments
        ] + [
            Competition(s, self._provider) for s in unique_stages
        ])


class Gender(str, Enum):
    UNSPECIFIED = "X"
    MALE = "M"
    FEMALE = "F"

    @classmethod
    def _missing_(cls, value):
        # This triggers if 'value' is not "X", "M", or "F".
        logger.debug(f"Received unknown gender value '{value}', defaulting to UNSPECIFIED")
        return cls.UNSPECIFIED
