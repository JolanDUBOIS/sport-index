from __future__ import annotations

from contextlib import suppress
from functools import cached_property
from typing import TYPE_CHECKING, Optional, Self, Any, Generic

import pycountry
from typing_extensions import TypeVar

from .base import IdentifiableEntity
from .collections import EntityCollection
from sportindex.exceptions import ProviderNotFoundError, EntityNotFoundError
from sportindex.provider.models import (
    _SportData,
    _CountryData,
    _CategoryData
)

if TYPE_CHECKING:
    from .competition import Competition
    from .event import Event
    from .leaderboard import Rankings
    from .types import SportContestNature
    from sportindex.provider import SofascoreProvider


E = TypeVar("E", bound="Event", default="Event")

class Sport(IdentifiableEntity, Generic[E]):
    """A sport (e.g., football, tennis, motorsport).

    Provides access to its categories and official rankings, and can be instantiated from minimal raw data without fetching full details.

    Attributes:
        id (int): Unique sport ID.
        name (str): Official sport name.
        slug (str): URL-friendly identifier.
        event_format (EventFormat): The event format for this sport (match-based or stage-based).
        categories (EntityCollection[Category[E]]): All categories associated with this sport.

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
    def nature(self) -> SportContestNature:
        """Determine the nature of the sport (opposition or comparison)."""
        from .static import SPORTS_REGISTRY
        for entry in SPORTS_REGISTRY:
            if entry.id == self.id:
                return entry.nature
        raise RuntimeError(f"Unexpected sport slug '{self.slug}' not found in SPORT_FORMATS mapping")

    @cached_property
    def categories(self) -> EntityCollection[Category[E]]:
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
    _REPR_FIELDS = ("id", "name", "slug", "alpha2", "alpha3")

    def __init__(self, data: _CountryData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _CountryData):
            raise TypeError(f"Country data must be of type _CountryData, got {type(data)}")

        self._pycountry_obj = kwargs.get("pycountry_obj")
        if not self._pycountry_obj:
            self._initialize_pycountry()

    def _initialize_pycountry(self) -> None:
        if self._data.alpha2:
            self._pycountry_obj = pycountry.countries.get(alpha_2=self._data.alpha2.upper())
        elif self._data.alpha3:
            self._pycountry_obj = pycountry.countries.get(alpha_3=self._data.alpha3.upper())
    
        if not self._pycountry_obj:
            try:
                self._pycountry_obj = pycountry.countries.lookup(self.name)
            except LookupError:
                pass

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
        return self._data.alpha2 or (getattr(self._pycountry_obj, "alpha_2", None) if self._pycountry_obj else None)

    @property
    def alpha3(self) -> Optional[str]:
        return self._data.alpha3 or (getattr(self._pycountry_obj, "alpha_3", None) if self._pycountry_obj else None)

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
        try:
            pycountry_obj = pycountry.countries.lookup(alpha.upper())
            return cls._from_pycountry(pycountry_obj, provider)
        except LookupError:
            raise EntityNotFoundError(f"Country with alpha code '{alpha}' not found in pycountry database")

    @classmethod
    def from_name(cls, name: str, provider: SofascoreProvider) -> Country:
        try:
            pycountry_obj = pycountry.countries.lookup(name)
            return cls._from_pycountry(pycountry_obj, provider)
        except LookupError:
            raise EntityNotFoundError(f"Country '{name}' not found in pycountry database")

    @classmethod
    def _from_pycountry(cls, pycountry_obj: Any, provider: SofascoreProvider) -> Country:
        return cls(
            data=_CountryData(
                name=pycountry_obj.name,
                slug=pycountry_obj.name.lower().replace(" ", "-"),
                alpha2=getattr(pycountry_obj, "alpha_2", None),
                alpha3=getattr(pycountry_obj, "alpha_3", None)
            ),
            provider=provider,
            pycountry_obj=pycountry_obj
        )


class Category(IdentifiableEntity, Generic[E]):
    """A category within a sport (e.g., 'France Amateur', 'Formula 1', 'International').

    Provides access to its sport, country (if applicable), and competitions.

    Attributes:
        id (int): Unique category ID.
        name (str): Category name.
        slug (str): URL-friendly identifier.
        sport (Sport): The sport this category belongs to.
        event_format (EventFormat): The event format for this category, derived from its sport.
        country (Country | None): The country this category belongs to, or None if international.
        competitions (EntityCollection[Competition[E]]]): All competitions under this category.
    
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
    def sport(self) -> Sport[E]:
        """The sport this category belongs to."""
        return Sport(self._data.sport, self._provider)

    @property
    def sport_nature(self) -> SportContestNature:
        """Determine the nature of the sport for this category."""
        return self.sport.nature

    @cached_property
    def country(self) -> Optional[Country]:
        """The country this category belongs to, or None if it's an international category."""
        if self._data.country:
            return Country(self._data.country, self._provider)

        if self._data.alpha2:
            with suppress(EntityNotFoundError):
                return Country.from_alpha(self._data.alpha2, self._provider)

        return None

    @cached_property
    def competitions(self) -> EntityCollection[Competition[E]]:
        """Fetch all competitions (unique tournaments / unique stages) for this category."""
        unique_tournaments = []
        with suppress(ProviderNotFoundError):
            unique_tournaments = self._provider.get_category_unique_tournaments(self.id)

        unique_stages = []
        with suppress(ProviderNotFoundError):
            unique_stages = self._provider.get_category_unique_stages(self.id)

        from .competition import Competition
        return EntityCollection(
            [Competition(c, self._provider) for c in unique_tournaments] +
            [Competition(s, self._provider) for s in unique_stages]
        )

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
