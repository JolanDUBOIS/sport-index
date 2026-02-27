from sportindex.core.base import BaseModel


# =====================================================================
# Common types
# =====================================================================

class ParsedScore(BaseModel):
    """Simple home/away score pair, used in parsed periods and incidents."""
    home: int
    away: int
