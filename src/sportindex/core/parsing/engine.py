from typing import TypeVar
from .registry import get_parser
from sportindex.core.base import BaseModel  

T = TypeVar('T')

def parse(node: T) -> T:
    """
    Recursively traverse and parse a model and all its nested fields.
    Uses a bottom-up approach: children are parsed before their parents.
    """
    if isinstance(node, list):
        return [parse(item) for item in node]
    if isinstance(node, dict):
        return {key: parse(value) for key, value in node.items()}

    if isinstance(node, BaseModel):
        # Walk down: recursively parse all fields first
        for field_name in node:
            original_value = getattr(node, field_name)
            parsed_value = parse(original_value)
            setattr(node, field_name, parsed_value)

        parser = get_parser(type(node))
        if parser:
            return parser(node)

    return node
