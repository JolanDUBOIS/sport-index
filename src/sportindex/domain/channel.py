from __future__ import annotations

from typing import TYPE_CHECKING

import pycountry

from .base import BaseEntity, IdentifiableEntity, EntityCollection
from sportindex.exceptions import EntityNotFoundError, ProviderNotFoundError, FetchError, DomainError
from sportindex.provider.parsed import ParsedChannel, ParsedCountryChannelsResponse

if TYPE_CHECKING:
    from .core import Country
    from .event import EventCollection
    from sportindex.provider.parsed import SofascoreProvider



class Channel(IdentifiableEntity[ParsedChannel]):
    """A TV channel broadcasting sports events.

    Provides access to the channel's name, ID, and scheduled events.

    Attributes:
        id (int): Unique channel ID.
        name (str): Channel name.
        events (EventCollection): Scheduled events broadcast on this channel.

    Raises:
        TypeError: If initialized with invalid data type.
        EntityNotFoundError: If channel does not exist in the provider.
        DomainError: If a network or provider error occurs during fetch.
    """
    _REPR_FIELDS = ("id", "name")

    def __init__(self, data: ParsedChannel, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, ParsedChannel):
            raise TypeError("Channel data must be of type ParsedChannel")

    @property
    def id(self) -> int:
        """The unique ID of the channel."""
        return self._data.id

    @property
    def name(self) -> str:
        """The name of the channel."""
        return self._data.name

    @property
    def events(self) -> EventCollection:
        """Fetch all scheduled events for this channel."""
        from .event import Event, EventCollection
        parsed_channel_events = self._provider.get_channel_schedule(self.id)
        return EventCollection([
            Event(e, self._provider) for e in parsed_channel_events.events
        ] + [
            Event(s, self._provider) for s in parsed_channel_events.stages
        ])

    @classmethod
    def from_id(cls, channel_id: int, provider: SofascoreProvider) -> Channel:
        """Fetch a channel by its ID."""
        try:
            parsed_channel_events = provider.get_channel_schedule(channel_id)
        except ProviderNotFoundError as e:
            raise EntityNotFoundError(f"Channel with id {channel_id} not found") from e
        except FetchError as e:
            raise DomainError(f"Network error while fetching channel {channel_id}") from e
        return cls(parsed_channel_events.channel, provider)


class EventChannels(BaseEntity[ParsedCountryChannelsResponse]):
    """Channels broadcasting a specific event, organized by country.

    Allows querying which channels broadcast the event in a given country.

    Attributes:
        channels (dict[str, list[int]]): Mapping from country alpha-2 codes to lists of channel IDs.

    Methods:
        get_channels(country, country_name, country_alpha): Return Channel entities broadcasting the event in a specific country.

    Raises:
        TypeError: If initialized with invalid data type.
        EntityNotFoundError: If a specified country cannot be found.
    """
    _REPR_FIELDS = ("channels")

    def __init__(self, data: ParsedCountryChannelsResponse, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, ParsedCountryChannelsResponse):
            raise TypeError("EventChannels data must be of type ParsedCountryChannelsResponse")

    @property
    def channels(self) -> dict[str, list[int]]:
        """A dictionary mapping country alpha-2 codes to lists of channel IDs broadcasting this event in that country."""
        return self._data.channels

    def get_channels(self, *, country: Country | None = None, country_name: str | None = None, country_alpha: str | None = None) -> EntityCollection[Channel]:
        """Get the channels broadcasting this event in a specific country (by object, name or alpha code)."""
        if country is not None:
            country_alpha2 = country.alpha2
        elif country_name is not None:
            country_obj = next(
                (c for c in pycountry.countries if c.name.lower() == country_name.lower()), None
            )
            if country_obj is None:
                raise EntityNotFoundError(f"Country with name '{country_name}' not found")
            country_alpha2 = country_obj.alpha_2
        elif country_alpha is not None:
            country_obj = next(
                (c for c in pycountry.countries if c.alpha_2 == country_alpha.upper() or c.alpha_3 == country_alpha.upper()),
                None
            )
            if country_obj is None:
                raise EntityNotFoundError(f"Country with alpha code '{country_alpha}' not found")
            country_alpha2 = country_obj.alpha_2
        else:
            raise TypeError("Must provide either country object, name or alpha code")
        return EntityCollection([Channel.from_id(cid, self._provider) for cid in self.channels.get(country_alpha2, [])])


# NOTE - Include votes for channels if available to improve potential recommendation system...²
