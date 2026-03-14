from __future__ import annotations

from typing import TYPE_CHECKING

import pycountry

from .base import BaseEntity, EntityCollection
from sportindex.core.provider.parsed import ParsedChannel, ParsedCountryChannelsResponse

if TYPE_CHECKING:
    from .core import Country
    from .event import EventCollection
    from sportindex.core.provider.parsed import ParsedSofascoreProvider



class Channel(BaseEntity[ParsedChannel]):
    """A TV channel broadcasting sports events."""
    REPR_FIELDS = ("id", "name")

    def __init__(self, data: ParsedChannel, provider: ParsedSofascoreProvider | None = None, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, ParsedChannel):
            raise ValueError("Channel data must be of type ParsedChannel")

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
    def from_id(cls, channel_id: int, provider: ParsedSofascoreProvider) -> Channel:
        """Fetch a channel by its ID."""
        parsed_channel_events = provider.get_channel_schedule(channel_id)
        return cls(parsed_channel_events.channel, provider)


class EventChannels(BaseEntity[ParsedCountryChannelsResponse]):
    """A wrapper for channels broadcasting an event, grouped by country."""
    REPR_FIELDS = ("id", "channels")

    def __init__(self, data: ParsedCountryChannelsResponse, provider: ParsedSofascoreProvider | None = None, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, ParsedCountryChannelsResponse):
            raise ValueError("EventChannels data must be of type ParsedCountryChannelsResponse")

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
                raise ValueError(f"Country with name '{country_name}' not found")
            country_alpha2 = country_obj.alpha_2
        elif country_alpha is not None:
            country_obj = next(
                (c for c in pycountry.countries if c.alpha_2 == country_alpha.upper() or c.alpha_3 == country_alpha.upper()),
                None
            )
            if country_obj is None:
                raise ValueError(f"Country with alpha code '{country_alpha}' not found")
            country_alpha2 = country_obj.alpha_2
        else:
            raise ValueError("Must provide either country object, name or alpha code")
        return EntityCollection([Channel.from_id(cid, self._provider) for cid in self.channels.get(country_alpha2, [])])


# NOTE - Include votes for channels if available to improve potential recommendation system...²
