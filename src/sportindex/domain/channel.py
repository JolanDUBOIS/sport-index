from __future__ import annotations

import logging
from typing import TYPE_CHECKING

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
        id (str): Unique channel ID.
        name (str): Channel name.
        events (EventCollection): Scheduled events broadcast on this channel.

    Raises:
        TypeError: If initialized with invalid data type.
        EntityNotFoundError: If channel does not exist in the provider.
        DomainError: If a network or provider error occurs during fetch.
    """
    _data: _ChannelData
    _PREFIX = "chl"
    _REPR_FIELDS = ("id", "name")

    def __init__(self, data: _ChannelData, provider: SofascoreProvider, **kwargs) -> None:
        super().__init__(data, provider, **kwargs)

        if not isinstance(data, _ChannelData):
            raise TypeError(f"Channel data must be of type _ChannelData, got {type(data)}")

    @property
    def id(self) -> str:
        """The unique ID of the channel."""
        return self.encode_id(self._data.id)

    @property
    def name(self) -> str:
        """The name of the channel."""
        return self._data.name

    def get_fixtures(self, silent: bool = False) -> EventCollection:
        """Fetch all scheduled events for this channel."""
        from .event import Event, EventCollection
        parsed_channel_events = self._provider.get_channel_schedule(self._data.id)
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

    @staticmethod
    def _fetch_entity(raw_id: int, provider: SofascoreProvider, **kwargs) -> _ChannelData:
        """Fetch the channel data from the provider by its raw ID."""
        try:
            parsed_channel_events = provider.get_channel_schedule(raw_id)
            return parsed_channel_events.channel
        except ProviderNotFoundError as e:
            logger.debug(f"Channel with id {raw_id} not found: {e}")
            raise EntityNotFoundError(f"Channel with id {raw_id} not found") from e
        except FetchError as e:
            logger.error(f"Network error while fetching channel with id {raw_id}: {e}")
            raise DomainError(f"Network error while fetching channel with id {raw_id}") from e
