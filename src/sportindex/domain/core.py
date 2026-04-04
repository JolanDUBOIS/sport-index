from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Optional, Self, Any

import pycountry

from .base import IdentifiableEntity, EntityCollection
from .types import EventFormat
from sportindex.exceptions import ProviderNotFoundError, EntityNotFoundError
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
    
    Class Methods:
        all(provider) -> EntityCollection[Sport]: Returns a collection of all supported sports.
        from_id(sport_id, provider) -> Sport: Create a Sport instance from its unique ID.
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
        from .static import SPORT_RANKINGS
        rankings = []
        for ranking_id, ranking_gender in SPORT_RANKINGS.get(self.slug, []):
            if gender is None or ranking_gender == gender:
                rankings.append(Rankings(
                    self._provider.get_ranking(ranking_id),
                    provider=self._provider,
                ))
        return rankings

    @classmethod
    def all(cls, provider: SofascoreProvider) -> EntityCollection[Sport]:
        """Returns a collection of all supported sports."""
        from .static import SPORTS_REGISTRY
        from sportindex.provider.models import _SportData

        return EntityCollection([
            cls(_SportData(id=s.id, slug=s.slug, name=s.name), provider)
            for s in SPORTS_REGISTRY
        ])

    @classmethod
    def from_id(cls, sport_id: int, provider: SofascoreProvider) -> Self:
        """Create a Sport instance from its unique ID."""
        sport = cls.all(provider).get(id=sport_id)
        if not sport:
            raise EntityNotFoundError(f"Sport with ID {sport_id} not found")
        return sport

    # NOTE - Look for a way to get fixtures for a sport if possible (without any category or competition context)...


class Country(IdentifiableEntity):
    """A country (e.g., France, England, Spain).

    Provides standard identifiers (name, slug, alpha-2, alpha-3) and can be instantiated from a name or alpha code.

    Attributes:
        id (int): The unique ID of the country.
        name (str): Official country name.
        slug (str): URL-friendly identifier.
        alpha2 (str | None): ISO alpha-2 code.
        alpha3 (str | None): ISO alpha-3 code.

    Class Methods:
        all(provider) -> EntityCollection[Country]: Fetch all countries.
        from_id(country_id: int, provider) -> Optional[Country]: Create from domain ID.
        from_alpha(alpha: str, provider) -> Optional[Country]: Create from alpha code.
        from_name(name: str, provider) -> Optional[Country]: Create from country name.

    Raises:
        ValueError: If the country cannot be found in the pycountry database.
    """
    _data: _CountryData
    _REPR_FIELDS = ("name", "slug", "alpha2", "alpha3")

    def __init__(self, data: _CountryData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _CountryData):
            raise TypeError(f"Country data must be of type _CountryData, got {type(data)}")

        self._pycountry_obj = kwargs.get("pycountry_obj")
        if not self._pycountry_obj:
            self._initialize_pycountry()

    def _initialize_pycountry(self) -> None:
        """Helper method to create _pycountry_obj from available data."""
        if self._data.alpha2:
            self._pycountry_obj = pycountry.countries.get(alpha_2=self._data.alpha2.upper())
        elif self._data.alpha3:
            self._pycountry_obj = pycountry.countries.get(alpha_3=self._data.alpha3.upper())
    
        if not self._pycountry_obj:
            search_name = self.name.lower()
            self._pycountry_obj = next(
                (c for c in pycountry.countries if c.name.lower() == search_name), 
                None
            )

        if not self._pycountry_obj:
            raise ValueError(f"Country '{self.name}' (slug: {self.slug}) not found in pycountry database")

    @property
    def id(self) -> int:
        """The ISO 3166-1 numeric code of the country."""
        return int(self._pycountry_obj.numeric)

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
        return self._data.alpha2 or (self._pycountry_obj.alpha_2 if self._pycountry_obj else None)

    @property
    def alpha3(self) -> Optional[str]:
        """The alpha-3 code of the country (e.g. 'FRA' for France)."""
        return self._data.alpha3 or (self._pycountry_obj.alpha_3 if self._pycountry_obj else None)

    @classmethod
    def all(cls, provider: SofascoreProvider) -> EntityCollection[Country]:
        """Fetch all countries."""
        return EntityCollection([
            cls._from_pycountry(c, provider)
            for c in pycountry.countries
        ])

    @classmethod
    def from_id(cls, country_id: int, provider: SofascoreProvider) -> Country:
        """Fetch a Country by its domain ID."""
        pycountry_obj = pycountry.countries.get(numeric=str(country_id).zfill(3))
        if not pycountry_obj:
            raise EntityNotFoundError(f"Country with ID '{country_id}' not found in pycountry database")
        return cls._from_pycountry(pycountry_obj, provider)

    @classmethod
    def from_alpha(cls, alpha: str, provider: SofascoreProvider) -> Country:
        """Create a Country instance from an alpha-2 or alpha-3 code."""
        pycountry_obj = pycountry.countries.get(alpha_2=alpha.upper()) or pycountry.countries.get(alpha_3=alpha.upper())
        if not pycountry_obj:
            raise EntityNotFoundError(f"Country with alpha code '{alpha}' not found in pycountry database")
        return cls._from_pycountry(pycountry_obj, provider)

    @classmethod
    def from_name(cls, name: str, provider: SofascoreProvider) -> Country:
        """Create a Country instance from a country name."""
        try:
            pycountry_obj = next(
                (c for c in pycountry.countries if c.name.lower() == name.lower())
            )
            return cls._from_pycountry(pycountry_obj, provider)
        except StopIteration:
            raise EntityNotFoundError(f"Country with name '{name}' not found in pycountry database")

    @classmethod
    def _from_pycountry(cls, pycountry_obj: Any, provider: SofascoreProvider) -> Country:
        """Helper method to populate country data from a pycountry object."""
        return cls(
            data=_CountryData(
                name=pycountry_obj.name,
                slug=pycountry_obj.name.lower().replace(" ", "-"),
                alpha2=pycountry_obj.alpha_2,
                alpha3=pycountry_obj.alpha_3
            ),
            provider=provider,
            pycountry_obj=pycountry_obj
        )


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
    
    Class Methods:
        all(provider) -> EntityCollection[Category]: Fetch all categories across all sports (expensive).
        from_id(category_id, provider) -> Category: Create a Category instance from its ID (expensive).
    """
    _data: _CategoryData
    _REPR_FIELDS = ("id", "name", "slug", "sport", "country")
    _all_cache: dict[int, EntityCollection[Category]] = {}

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

    @classmethod
    def all(cls, provider: SofascoreProvider) -> EntityCollection[Category]:
        """
        Returns a collection of all categories across all sports.
        Warning: This requires N API calls (one per sport) on the first call to build the cache.
        """
        provider_key = id(provider)

        if provider_key not in cls._all_cache:
            all_categories = []
            for sport in Sport.all(provider):
                all_categories.extend(sport.categories)
            cls._all_cache[provider_key] = EntityCollection(all_categories)

        return cls._all_cache[provider_key]

    @classmethod
    def from_id(cls, category_id: int, provider: SofascoreProvider) -> Self:
        """
        Create a Category instance from its ID.
        Warning: This requires N API calls (one per sport) on the first call to build the cache.
        """
        category = cls.all(provider).get(id=category_id)
        if not category:
            raise EntityNotFoundError(f"Category with ID {category_id} not found")
        return category
