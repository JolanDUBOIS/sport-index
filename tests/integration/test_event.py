import logging
from datetime import date, datetime

import sportindex
from sportindex import (
    Event,
    MatchEvent,
    StageEvent,
)
from sportindex.api_client import SofascoreProvider

logger = logging.getLogger(__name__)

def test_event(provider: SofascoreProvider):
    """Test that the Event entity behaves correctly."""
    logger.info("Testing Event entity...")

    # Match Event
    logger.info("Testing MatchEvent...")
    event = Event.from_id(31262682, provider)
    assert isinstance(event, MatchEvent)
    assert event.id == 31262682
    assert event.name == "Paris Saint Germain Chelsea"
    assert event.slug == "paris-saint-germain-chelsea"
    assert isinstance(event.start, datetime)
    assert event.start.date() == date(2026, 3, 11)
    assert isinstance(event.status, sportindex.EventStatus)
    assert event.status.type == "finished"
    assert event.competition.id == 14
    assert event.season.id == 281475211668633
    assert event.venue.id == 1686
    assert event.score.home == 5 and event.score.away == 2
    assert event.winner.id == 3288
    assert len(event.periods) == 2
    assert all(isinstance(period, sportindex.MatchPeriod) for period in event.periods)
    assert isinstance(event.lineups, sportindex.MatchLineups) or event.lineups is None
    assert len(event.incidents) > 0
    assert all(isinstance(incident.incident_type, str) for incident in event.incidents)
    assert len(event.statistics) > 0
    assert all(isinstance(stat, sportindex.PeriodStats) for stat in event.statistics)
    assert all(isinstance(point, sportindex.MomentumPoint) for point in event.momentum_graph)
    assert len(event.h2h) > 0
    assert isinstance(event.h2h, sportindex.EventCollection)
    assert all(h2h_event.competitors.home.id == 3288 or h2h_event.competitors.away.id == 3288 for h2h_event in event.h2h)
    assert all(isinstance(channel, sportindex.Channel) for channel in event.get_channels("FR"))

    # Stage Event
    logger.info("Testing StageEvent...")
    event = Event.from_id(428311, provider)
    assert isinstance(event, StageEvent)
    assert event.id == 428311
    assert event.name == "Japan GP"
    assert event.slug == "japan-gp"
    assert isinstance(event.start, datetime)
    assert isinstance(event.end, datetime)
    assert abs(event.end.date() - event.start.date()).days <= 4
    assert isinstance(event.status, sportindex.EventStatus)
    assert event.status.type == "finished"
    assert event.tier.name.lower() == "event"
    assert event.competition.id == 81
    assert event.season.id == 562951312589948
    assert event.parent is None
    assert len(event.substages) > 0
    assert all(subevent.parent == event for subevent in event.substages)
    assert isinstance(event.venue, sportindex.Venue)
    assert isinstance(event.winner, sportindex.Competitor)
    assert all(isinstance(standings, sportindex.Standings) for standings in event.standings)
    assert all(isinstance(channel, sportindex.Channel) for channel in event.get_channels("FR"))
