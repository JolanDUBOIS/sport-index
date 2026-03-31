from typing import Any
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, model_validator
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        extra='ignore', 
        populate_by_name=True,
        alias_generator=to_camel
    )

    @model_validator(mode='before')
    @classmethod
    def scrub_data(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {
                k: v for k, v in data.items() 
                if v is not None and v != {}
            }
        return data

    @model_validator(mode='after')
    def enforce_global_utc(self):
        for field_name, field_value in self:
            if isinstance(field_value, datetime):
                if field_value.tzinfo is None:
                    setattr(self, field_name, field_value.replace(tzinfo=timezone.utc))
                else:
                    setattr(self, field_name, field_value.astimezone(timezone.utc))
        return self
