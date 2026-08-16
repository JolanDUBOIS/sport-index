import logging
from datetime import datetime

import sportindex
from sportindex import SportClient, Standings
from sportindex.api_client import SofascoreProvider

logger = logging.getLogger(__name__)

def test_standings(client: SportClient, provider: SofascoreProvider):
    """Test that the Standings entity behaves correctly."""
    ucl = client.get("trnc:7", sportindex.Competition)

    # Pinned to a completed season on purpose. seasons[0] is the *newest* season, which the
    # provider creates months before it kicks off — it has no standings until then, so using
    # it makes this test fail every off-season.
    ucl_season = ucl.seasons.get(id="trnc:7:trns:61644", strict=True)  # 2024/25
    standings = ucl_season.standings
    assert all(isinstance(s, Standings) for s in standings)
    assert len(standings) == 3

    total_standings = next((s for s in standings if s.kind == "total"), None)
    assert total_standings is not None
    assert total_standings.name is not None
    assert isinstance(total_standings.updated_at, datetime) or total_standings.updated_at is None
    assert total_standings.sport.id == "spt:1"
    assert len(total_standings.entries) > 30

def test_rankings(client: SportClient, provider: SofascoreProvider):
    """Test that the Rankings entity behaves correctly."""
    mma = client.get("spt:76", sportindex.Sport)
    mma_rankings = mma.get_rankings()
    assert all(isinstance(r, sportindex.Rankings) for r in mma_rankings)
    assert len(mma_rankings) > 0
    for ranking in mma_rankings:
        assert ranking.name is not None
        assert isinstance(ranking.updated_at, datetime) or ranking.updated_at is None
        assert ranking.gender in ("M", "F")
        assert all(isinstance(e, sportindex.RankingsEntry) for e in ranking.entries)
        assert ranking.sport.id == "spt:76"

def test_rankings_with_unlinked_entrants(client: SportClient, provider: SofascoreProvider):
    """Rankings list entrants the provider has no team page for, without dropping rows.

    The rugby league table backs only its top 20 with teams; the rest carry a name alone.
    Those must still come through, or positions stop matching the published ranking.
    """
    rugby = client.get("spt:12", sportindex.Sport)
    rugby_league = next(r for r in rugby.get_rankings() if r.id == 4)

    entries = rugby_league.entries
    assert len(entries) == 35
    assert [e.position for e in entries] == list(range(1, 36))
    assert all(e.name for e in entries)

    linked = [e for e in entries if isinstance(e.entity, sportindex.Competitor)]
    countries = [e for e in entries if isinstance(e.entity, sportindex.Country)]
    assert len(linked) == 20
    assert len(countries) == 15

    # Entrants without a team resolve to the ISO country of the same name.
    germany = next(e for e in entries if e.name == "Germany")
    assert germany.entity.id == "ctr:276"
    assert germany.points == 23
