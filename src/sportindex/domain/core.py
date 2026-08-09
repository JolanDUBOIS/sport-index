from __future__ import annotations

import logging
from contextlib import suppress
from functools import cached_property
from typing import TYPE_CHECKING, Any, Self

import pycountry

from sportindex.api_client.models import _CategoryData, _CountryData, _SportData
from sportindex.exceptions import (
    DomainError,
    EntityNotFoundError,
    FetchError,
    ProviderNotFoundError,
)

from .base import IdentifiableEntity
from .collections import EntityCollection

if TYPE_CHECKING:
    from sportindex.api_client import SofascoreProvider

    from .competition import Competition
    from .leaderboard import Rankings

logger = logging.getLogger(__name__)


class Sport(IdentifiableEntity):
    """A sport, such as football, tennis or motorsport.

    Sports come from a fixed built-in registry rather than from the provider, so a Sport
    is always complete: there is nothing further to load.

    Attributes:
        id (str): Globally unique SDK ID, e.g. "spt:1".
        name (str): Display name, e.g. "Football".
        slug (str): URL-friendly identifier, e.g. "football".
        categories (EntityCollection[Category]): Every category grouping this sport's
            competitions — countries, international bodies, and the like.
        source (_SportData): The parsed payload backing this entity. (inherited from BaseEntity)

    Methods:
        get_rankings(gender: str | None = None) -> list[Rankings]: The sport's official
            ranking tables — FIFA, ATP, WTA, UFC divisions. Pass "M" or "F" to keep only
            that gender's tables. Empty for sports with no known rankings.
        all(provider: SofascoreProvider) -> EntityCollection[Sport]: Every supported sport. (classmethod)
        from_id(entity_id: str, provider: SofascoreProvider) -> Sport: The sport with this SDK ID. (classmethod)

    Raises:
        TypeError: If constructed with data that is not `_SportData`.
        EntityNotFoundError: If `from_id` is given an ID no supported sport carries.
        DomainError: If the provider fails while resolving the sport.
    """
    _data: _SportData
    _PREFIX = "spt"
    _REPR_FIELDS = ("id", "name", "slug")

    def __init__(self, data: _SportData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _SportData):
            raise TypeError(f"Sport data must be of type _SportData, got {type(data)}")

    @property
    def id(self) -> str:
        """The unique ID of the sport."""
        return self.encode_id(self._data.id)

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

    def get_rankings(self, gender: str | None = None) -> list[Rankings]:
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
        from sportindex.api_client.models import _SportData

        from .static import SPORTS_REGISTRY
        return EntityCollection([
            cls(_SportData(id=s.id, slug=s.slug, name=s.name), provider)
            for s in SPORTS_REGISTRY
        ])

    @classmethod
    def from_id(cls, entity_id: str, provider: SofascoreProvider) -> Self:
        """Create a Sport instance from its unique ID."""
        try:
            sport = cls.all(provider).get(id=entity_id)
            if not sport:
                raise EntityNotFoundError(f"Sport with ID {entity_id} not found")
            return sport
        except ProviderNotFoundError as e:
            raise EntityNotFoundError(f"Sport with ID {entity_id} not found") from e
        except FetchError as e:
            raise DomainError(f"Error fetching sport with ID {entity_id}") from e

    @staticmethod
    def _fetch_entity(raw_id: int, provider: SofascoreProvider, **kwargs) -> _SportData:
        raise NotImplementedError("Sport entities are not fetched by ID and are instead instantiated from static data.")

    def _full_load(self) -> None:
        """Sport entities are always fully loaded at construction time; nothing more to fetch."""
        self._full_loaded = True


class Country(IdentifiableEntity):
    """A country, such as France, England or Spain.

    Every Country is backed by an ISO 3166-1 record, so its codes are canonical even when
    the provider supplied only a name or a partial payload. A Country is always complete:
    there is nothing further to load.

    Attributes:
        id (str): Globally unique SDK ID built from the ISO 3166-1 numeric code, e.g. "ctr:250".
        name (str): Title-cased country name, e.g. "France".
        slug (str): URL-friendly identifier, e.g. "france".
        alpha2 (str | None): ISO 3166-1 alpha-2 code, e.g. "FR".
        alpha3 (str | None): ISO 3166-1 alpha-3 code, e.g. "FRA".
        source (_CountryData): The parsed payload backing this entity. (inherited from BaseEntity)

    Methods:
        all(provider: SofascoreProvider) -> EntityCollection[Country]: Every ISO 3166-1 country. (classmethod)
        from_id(entity_id: str, provider: SofascoreProvider) -> Country: The country with this SDK ID. (classmethod)
        from_alpha(alpha: str, provider: SofascoreProvider) -> Country: The country with this alpha-2
            or alpha-3 code. (classmethod)
        from_name(name: str, provider: SofascoreProvider) -> Country: The country with this name. (classmethod)

    Raises:
        TypeError: If constructed with data that is not `_CountryData`.
        ValueError: If the payload matches no ISO 3166-1 record.
        EntityNotFoundError: If `from_id`, `from_alpha` or `from_name` matches no ISO 3166-1 record.
    """
    _data: _CountryData
    _PREFIX = "ctr"
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
            with suppress(LookupError):
                self._pycountry_obj = pycountry.countries.lookup(self.name)

        if not self._pycountry_obj:
            raise ValueError(f"Country '{self.name}' (slug: {self.slug}) not found in pycountry database")

    @property
    def id(self) -> str:
        """The ISO 3166-1 numeric code of the country."""
        return self.encode_id(self._pycountry_obj.numeric)

    @property
    def name(self) -> str:
        """The name of the country."""
        return self._data.name.title() or self._data.slug.replace("-", " ").title()

    @property
    def slug(self) -> str:
        """The slug of the country (used in URLs)."""
        return self._data.slug

    @property
    def alpha2(self) -> str | None:
        return self._data.alpha2 or (getattr(self._pycountry_obj, "alpha_2", None) if self._pycountry_obj else None)

    @property
    def alpha3(self) -> str | None:
        return self._data.alpha3 or (getattr(self._pycountry_obj, "alpha_3", None) if self._pycountry_obj else None)

    @classmethod
    def all(cls, provider: SofascoreProvider) -> EntityCollection[Country]:
        """Fetch all countries."""
        return EntityCollection([
            cls._from_pycountry(c, provider)
            for c in pycountry.countries
        ])

    @classmethod
    def from_id(cls, entity_id: str, provider: SofascoreProvider) -> Country:
        """Fetch a Country by its domain ID."""
        try:
            _, _, raw_id = cls.decode_id(entity_id)
            pycountry_obj = pycountry.countries.get(numeric=str(raw_id).zfill(3))
            if not pycountry_obj:
                raise EntityNotFoundError(f"Country with ID '{entity_id}' not found in pycountry database")
            return cls._from_pycountry(pycountry_obj, provider)
        except LookupError as e:
            raise EntityNotFoundError(f"Country with ID '{entity_id}' not found in pycountry database") from e

    @classmethod
    def from_alpha(cls, alpha: str, provider: SofascoreProvider) -> Country:
        try:
            pycountry_obj = pycountry.countries.lookup(alpha.upper())
            return cls._from_pycountry(pycountry_obj, provider)
        except LookupError as e:
            raise EntityNotFoundError(f"Country with alpha code '{alpha}' not found in pycountry database") from e

    @classmethod
    def from_name(cls, name: str, provider: SofascoreProvider) -> Country:
        try:
            pycountry_obj = pycountry.countries.lookup(name)
            return cls._from_pycountry(pycountry_obj, provider)
        except LookupError as e:
            raise EntityNotFoundError(f"Country '{name}' not found in pycountry database") from e

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

    @staticmethod
    def _fetch_entity(raw_id: int, provider: SofascoreProvider, **kwargs) -> _SportData:
        raise NotImplementedError("Country entities are not fetched by ID and are instead instantiated from pycountry data.")

    def _full_load(self) -> None:
        """Country entities are always fully loaded at construction time; nothing more to fetch."""
        self._full_loaded = True


class Category(IdentifiableEntity):
    """A grouping of competitions within a sport, e.g. 'France Amateur', 'Formula 1', 'International'.

    Categories are the level between a sport and its competitions. Most are countries; the
    rest are international or organiser-level groupings.

    Attributes:
        id (str): Globally unique SDK ID, e.g. "cat:7".
        name (str): Display name, e.g. "France".
        slug (str): URL-friendly identifier, e.g. "france".
        sport (Sport): The sport this category sits under.
        country (Country | None): The country this category represents, or None for
            international and organiser-level categories.
        competitions (EntityCollection[Competition]): Every competition in this category,
            covering both match-based tournaments and stage-based competitions. Empty when
            the provider lists neither.
        source (_CategoryData): The parsed payload backing this entity. (inherited from BaseEntity)

    Methods:
        all(provider: SofascoreProvider) -> EntityCollection[Category]: Every category across every
            sport. Cached per provider; the first call is slow. (classmethod)
        from_id(entity_id: str, provider: SofascoreProvider) -> Category: The category with this SDK
            ID. Shares the `all()` cache, so the first call is slow. (classmethod)

    Raises:
        TypeError: If constructed with data that is not `_CategoryData`.
        EntityNotFoundError: If `from_id` is given an ID no category carries.
        DomainError: If the provider fails while resolving the category.
    """
    _data: _CategoryData
    _PREFIX = "cat"
    _REPR_FIELDS = ("id", "name", "slug", "sport", "country")
    _all_cache: dict[int, EntityCollection[Category]] = {}

    def __init__(self, data: _CategoryData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _CategoryData):
            raise TypeError(f"Category data must be of type _CategoryData, got {type(data)}")

    @property
    def id(self) -> str:
        """The unique ID of the category."""
        return self.encode_id(self._data.id)

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
    def country(self) -> Country | None:
        """The country this category belongs to, or None if it's an international category."""
        if self._data.country:
            return Country(self._data.country, self._provider)

        if self._data.alpha2:
            with suppress(EntityNotFoundError):
                return Country.from_alpha(self._data.alpha2, self._provider)

        return None

    @cached_property
    def competitions(self) -> EntityCollection[Competition]:
        """Fetch all competitions (unique tournaments / unique stages) for this category."""
        unique_tournaments = []
        with suppress(ProviderNotFoundError):
            unique_tournaments = self._provider.get_category_unique_tournaments(self._data.id)

        unique_stages = []
        with suppress(ProviderNotFoundError):
            unique_stages = self._provider.get_category_unique_stages(self._data.id)

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
                logger.debug(f"Fetching categories for sport '{sport.name}' (ID: {sport.id})...")
                all_categories.extend(sport.categories)
            cls._all_cache[provider_key] = EntityCollection(all_categories)

        return cls._all_cache[provider_key]

    @classmethod
    def from_id(cls, entity_id: str, provider: SofascoreProvider) -> Self:
        """
        Create a Category instance from its ID.
        Warning: This requires N API calls (one per sport) on the first call to build the cache.
        """
        try:
            category = cls.all(provider).get(id=entity_id)
            if not category:
                raise EntityNotFoundError(f"Category with ID {entity_id} not found")
            return category
        except ProviderNotFoundError as e:
            raise EntityNotFoundError(f"Category with ID {entity_id} not found") from e
        except FetchError as e:
            raise DomainError(f"Error fetching category with ID {entity_id}") from e

    @staticmethod
    def _fetch_entity(raw_id: int, provider: SofascoreProvider, **kwargs) -> _CategoryData:
        raise NotImplementedError("Category entities are not fetched by ID and are instead instantiated from related sport data.")

    def _full_load(self) -> None:
        """Category entities are always fully loaded at construction time; nothing more to fetch."""
        self._full_loaded = True
