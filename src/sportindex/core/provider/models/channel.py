from __future__ import annotations
from dataclasses import dataclass

from .core import BaseModel
from .event import Event
from .stage import Stage


@dataclass(frozen=True, kw_only=True)
class CountryChannel:
    country_code: str
    channel_ids: list[str]

@dataclass(frozen=True, kw_only=True)
class CountryChannels(BaseModel):
    channels: list[CountryChannel]

    @classmethod
    def _from_api(cls, raw: dict) -> CountryChannels:
        channels = []
        for code, channel_ids in raw.get("channels", {}).items():
            channels.append(CountryChannel(country_code=code, channel_ids=channel_ids))
        return CountryChannels(channels=channels)

@dataclass(frozen=True, kw_only=True)
class Channel(BaseModel):
    id: str
    name: str

    @classmethod
    def _from_api(cls, raw: dict) -> Channel:
        return Channel(
            id=raw.get("id"),
            name=raw.get("name"),
        )

@dataclass(frozen=True, kw_only=True)
class ChannelSchedule(BaseModel):
    channel: Channel
    events: list[Event]
    stages: list[Stage]

    @classmethod
    def _from_api(cls, raw: dict) -> ChannelSchedule:
        return ChannelSchedule(
            channel=Channel.from_api(raw.get("channel")),
            events=[Event.from_api(event) for event in raw.get("events", [])],
            stages=[Stage.from_api(stage) for stage in raw.get("stages", [])]
        )
