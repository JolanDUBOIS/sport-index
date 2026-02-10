from datetime import datetime
from typing import Optional, Literal


def timestamp_to_iso(
    ts: Optional[float],
    kind: Literal["date", "datetime"] = "datetime",
) -> Optional[str]:
    if ts is None:
        return None

    dt = datetime.fromtimestamp(ts)

    if kind == "date":
        return dt.date().isoformat()

    return dt.isoformat(timespec="seconds")

def get_nested(data: dict, path: str, default = None) -> any:
    current = data
    for key in path.split("."):
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current
