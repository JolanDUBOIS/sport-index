from datetime import datetime, timezone

from sportindex.core.models import Timestamp, ISODate


def parse_timestamp(ts: Timestamp | int | float | None) -> datetime | None:
    """Convert a Unix timestamp to datetime. Returns None if ts is None."""
    if ts is None:
        return None
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt


def parse_iso(value: ISODate | str | None) -> datetime | None:
    """Convert ISO 8601 string to datetime (UTC). Returns None if value is None."""
    if value is None:
        return None
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt
