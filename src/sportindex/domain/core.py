from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Optional

import pycountry

from .base import BaseEntity, IdentifiableEntity, EntityCollection
from .static import SPORT_RANKINGS
from .types import EventFormat
from sportindex.exceptions import ProviderNotFoundError
from sportindex.provider.models import (
    _SportData,
    _CountryData,
    _CategoryData
)

if TYPE_CHECKING:
    from .competition import Competition
    from .leaderboard import Rankings
    from sportindex.provider import SofascoreProvider


class Sport(IdentifiableEntity):
    """A sport (e.g., football, tennis, motorsport).

    Provides access to its categories and official rankings, and can be instantiated from minimal raw data without fetching full details.

    Attributes:
        id (int): Unique sport ID.
        name (str): Official sport name.
        slug (str): URL-friendly identifier.
        format (EventFormat): The event format for this sport (match-based or stage-based).
        categories (EntityCollection[Category]): All categories associated with this sport.

    Methods:
        get_rankings(gender: Optional[str] = None) -> list[Rankings]: Fetch official rankings for the sport.
    """
    _data: _SportData
    _REPR_FIELDS = ("id", "name", "slug")

    def __init__(self, data: _SportData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _SportData):
            raise TypeError(f"Sport data must be of type _SportData, got {type(data)}")

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
    def format(self) -> EventFormat:
        """Determine the event format for this sport (match-based or stage-based)."""
        # TODO - This information will be imported from static one way or another...
        raise NotImplementedError("Sport format detection is not implemented yet")

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
    def _from_tuple(cls, data: tuple[int, str, str], provider: SofascoreProvider) -> Sport:
        """
        Create a Sport instance from a raw tuple (id, slug, name).
        This is used to build the initial list of sports without needing to fetch categories or rankings.
        """
        sid, slug, name = data
        return cls(_SportData(id=sid, slug=slug, name=name), provider)

    @classmethod
    def from_id(cls, sport_id: int, provider: SofascoreProvider) -> Optional[Sport]:
        """Create a Sport instance from its unique ID."""
        from .static import _SPORTS_DATA
        data = next((s for s in _SPORTS_DATA if s[0] == sport_id), None)
        return cls._from_tuple(data, provider) if data else None

    # NOTE - Look for a way to get fixtures for a sport if possible (without any category or competition context)...


class Country(BaseEntity):
    """A country (e.g., France, England, Spain).

    Provides standard identifiers (name, slug, alpha-2, alpha-3) and can be instantiated from a name or alpha code.

    Attributes:
        name (str): Official country name.
        slug (str): URL-friendly identifier.
        alpha2 (str | None): ISO alpha-2 code.
        alpha3 (str | None): ISO alpha-3 code.

    Methods:
        from_alpha(alpha: str, provider) -> Optional[Country]: Create from alpha code.
        from_name(name: str, provider) -> Optional[Country]: Create from country name.
    """
    _data: _CountryData
    _REPR_FIELDS = ("name", "slug", "alpha2", "alpha3")

    def __init__(self, data: _CountryData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _CountryData):
            raise TypeError(f"Country data must be of type _CountryData, got {type(data)}")

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
    def from_alpha(cls, alpha: str, provider: SofascoreProvider) -> Optional[Country]:
        """Create a Country instance from an alpha-2 or alpha-3 code."""
        country = next(
            (c for c in pycountry.countries if c.alpha_2 == alpha.upper() or c.alpha_3 == alpha.upper()), None
        )
        if country:
            return cls(
                data=_CountryData(
                    name=country.name,
                    slug=country.name.lower().replace(" ", "-"),
                    alpha2=country.alpha_2,
                    alpha3=country.alpha_3
                ),
                provider=provider
            )
        return None

    @classmethod
    def from_name(cls, name: str, provider: SofascoreProvider) -> Optional[Country]:
        """Create a Country instance from a country name."""
        country = next(
            (c for c in pycountry.countries if c.name.lower() == name.lower()), None
        )
        if country:
            return cls(
                data=_CountryData(
                    name=country.name,
                    slug=country.name.lower().replace(" ", "-"),
                    alpha2=country.alpha_2,
                    alpha3=country.alpha_3
                ),
                provider=provider
            )
        return None


class Category(IdentifiableEntity):
    """A category within a sport (e.g., 'France Amateur', 'Formula 1', 'International').

    Provides access to its sport, country (if applicable), and competitions.

    Attributes:
        id (int): Unique category ID.
        name (str): Category name.
        slug (str): URL-friendly identifier.
        sport (Sport): The sport this category belongs to.
        format (EventFormat): The event format for this category, derived from its sport.
        country (Country | None): The country this category belongs to, or None if international.
        competitions (EntityCollection[Competition]): All competitions under this category.
    """
    _data: _CategoryData
    _REPR_FIELDS = ("id", "name", "slug", "sport", "country")

    def __init__(self, data: _CategoryData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _CategoryData):
            raise TypeError(f"Category data must be of type _CategoryData, got {type(data)}")

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

    @property
    def format(self) -> EventFormat:
        """Determine the event format for this category based on its sport."""
        return self.sport.format

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
