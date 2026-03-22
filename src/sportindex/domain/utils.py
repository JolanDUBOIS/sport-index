from typing import TypeVar, Optional
from dataclasses import replace, fields, is_dataclass


T = TypeVar("T")

def merge_dataclasses(base_obj: T, new_obj: Optional[T]) -> T:
    """Merge two dataclass instances of the same type, preferring non-None values from new_obj."""
    if new_obj is None:
        return base_obj

    if type(base_obj) is not type(new_obj):
        raise ValueError("Both objects must be of the same dataclass type")
    if not is_dataclass(base_obj) or not is_dataclass(new_obj):
        raise ValueError("Both objects must be dataclass instances")

    updates = {
        f.name: getattr(new_obj, f.name) 
        for f in fields(new_obj) 
        if getattr(new_obj, f.name) is not None
    }
    
    return replace(base_obj, **updates)
