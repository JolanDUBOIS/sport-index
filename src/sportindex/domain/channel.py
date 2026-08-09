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

    A channel exposes only its identity and its forward-looking schedule; the provider keeps
    no broadcast history, so past events are not available.

    Attributes:
        id (str): Globally unique SDK ID, e.g. "chl:58".
        name (str): Channel name, e.g. "Canal+".
        source (_ChannelData): The parsed payload backing this entity. (inherited from BaseEntity)

    Methods:
        get_fixtures(silent: bool = False) -> EventCollection: The channel's upcoming schedule,
            mixing `MatchEvent` and `StageEvent`.
        get_results(silent: bool = False) -> EventCollection: Always empty — the provider exposes
            no broadcast history for a channel. Logs a warning unless `silent` is True.
        get_events() -> EventCollection: Fixtures and results combined, sorted by start time.
            In practice equal to `get_fixtures()`, since results are always empty.
            (inherited from EventAwareMixin)
        from_id(entity_id: str, provider: SofascoreProvider) -> Channel: The channel with this SDK
            ID. (classmethod, inherited from IdentifiableEntity)

    Raises:
        TypeError: If constructed with data that is not `_ChannelData`.
        EntityNotFoundError: If `from_id` names a channel the provider does not have.
        DomainError: If the provider fails with a network or transport error.
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
