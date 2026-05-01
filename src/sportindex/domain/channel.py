from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Self

from sportindex.api_client.models import _ChannelData
from sportindex.exceptions import (
    DomainError,
    EntityNotFoundError,
    FetchError,
    ProviderNotFoundError,
)

from .base import IdentifiableEntity
from .event import EventAwareMixin

if TYPE_CHECKING:
    from sportindex.api_client import SofascoreProvider

    from .event import EventCollection

logger = logging.getLogger(__name__)


class Channel(IdentifiableEntity, EventAwareMixin):
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
    _data: _ChannelData
    _REPR_FIELDS = ("id", "name")

    def __init__(self, data: _ChannelData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _ChannelData):
            raise TypeError(f"Channel data must be of type _ChannelData, got {type(data)}")

    @property
    def id(self) -> int:
        """The unique ID of the channel."""
        return self._data.id

    @property
    def name(self) -> str:
        """The name of the channel."""
        return self._data.name

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Fetch all scheduled events for this channel."""
        from .event import Event, EventCollection
        parsed_channel_events = self._provider.get_channel_schedule(self.id)
        return EventCollection([
            Event(e, self._provider) for e in parsed_channel_events.events
        ] + [
            Event(s, self._provider) for s in parsed_channel_events.stages
        ])

    def get_results(self, silent: bool = False) -> EventCollection:
        """Fetch all past events for this channel."""
        from .event import EventCollection
        if not silent:
            logger.warning("get_results for Channel is not supported, returning empty list")
        return EventCollection()

    @classmethod
    def from_id(cls, channel_id: int, provider: SofascoreProvider) -> Self:
        """Fetch a channel by its ID."""
        if not isinstance(channel_id, int):
            raise TypeError(f"Channel ID must be an integer, got {type(channel_id)}")
        try:
            parsed_channel_events = provider.get_channel_schedule(channel_id)
            return cls(parsed_channel_events.channel, provider)
        except ProviderNotFoundError as e:
            raise EntityNotFoundError(f"Channel with id {channel_id} not found") from e
        except FetchError as e:
            raise DomainError(f"Network error while fetching channel {channel_id}") from e
