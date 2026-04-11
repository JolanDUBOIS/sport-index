import logging
from datetime import datetime

import sportindex
from sportindex import SportClient, Standings
from sportindex.provider import SofascoreProvider


logger = logging.getLogger(__name__)

def test_standings(client: SportClient, provider: SofascoreProvider):
    """Test that the Standings entity behaves correctly."""
    ucl = client.get(sportindex.Competition, 14)

    ucl_season = ucl.seasons[0] # Get the current season for testing
    standings = ucl_season.standings
    assert all(isinstance(s, Standings) for s in standings)
    assert len(standings) == 3

    total_standings = next((s for s in standings if s.kind == "total"), None)
    assert total_standings is not None
    assert total_standings.name is not None
    assert isinstance(total_standings.updated_at, datetime) or total_standings.updated_at is None
    assert total_standings.sport.id == 1
    assert len(total_standings.entries) > 30

def test_rankings(client: SportClient, provider: SofascoreProvider):
    """Test that the Rankings entity behaves correctly."""
    mma = client.get(sportindex.Sport, 76)
    mma_rankings = mma.get_rankings()
    assert all(isinstance(r, sportindex.Rankings) for r in mma_rankings)
    assert len(mma_rankings) > 0
    for ranking in mma_rankings:
        assert ranking.name is not None
        assert isinstance(ranking.updated_at, datetime) or ranking.updated_at is None
        assert ranking.gender in ("M", "F")
        assert all(isinstance(e, sportindex.RankingsEntry) for e in ranking.entries)
        assert ranking.sport.id == 76
