from typing import TypedDict


# =====================================================================
# Common types
# =====================================================================

class ParsedScore(TypedDict, total=False):
    """Simple home/away score pair, used in parsed periods and incidents."""
    home: int | None
    away: int | None
