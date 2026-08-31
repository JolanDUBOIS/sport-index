from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator
from pydantic.alias_generators import to_camel

from sportindex._repr import PydanticReprMixin


class BaseSchema(PydanticReprMixin, BaseModel):
    """Base for every parsed provider payload.

    Rendering comes from `PydanticReprMixin`: a schema shows whichever of id, name and slug
    it declares rather than pydantic's full recursive dump, which for a payload such as a
    team runs to several hundred characters of nested models.
    """

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
                    setattr(self, field_name, field_value.replace(tzinfo=UTC))
                else:
                    setattr(self, field_name, field_value.astimezone(UTC))
        return self
