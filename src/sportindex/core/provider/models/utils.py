from datetime import datetime, timezone
from typing import Optional, Literal


def timestamp_to_iso(
    ts: Optional[float],
    kind: Literal["date", "datetime"] = "datetime",
) -> Optional[str]:
    if ts is None:
        return None

    dt = datetime.fromtimestamp(ts, tz=timezone.utc)

    if kind == "date":
        return dt.date().isoformat()

    return dt.isoformat(timespec="seconds")

def iso_to_iso(
    value: Optional[str],
    kind: Literal["date", "datetime"] = "datetime",
) -> Optional[str]:
    if value is None:
        return None

    dt = datetime.fromisoformat(value)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

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
