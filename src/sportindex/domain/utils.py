from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from pydantic import BaseModel


T = TypeVar("T", bound="BaseModel")

def merge_pydantic_models(base_obj: T, new_obj: T | None) -> T:
    """Merge two Pydantic models, preferring non-None values from new_obj."""
    if new_obj is None:
        return base_obj

    if type(base_obj) is not type(new_obj):
        raise TypeError(f"Both objects must be of the same Pydantic model type, got {type(base_obj)} and {type(new_obj)}")

    base_dict = base_obj.model_dump()
    updates = new_obj.model_dump(exclude_none=True)

    merged_dict = base_dict | updates

    return type(base_obj).model_validate(merged_dict, context={"preprocessed": True})
