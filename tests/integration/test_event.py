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
    event = Event.from_id("mch:15631341", provider)
    assert isinstance(event, MatchEvent)
    assert event.id == "mch:15631341"
    assert event.name == "Paris Saint Germain Chelsea"
    assert event.slug == "paris-saint-germain-chelsea"
    assert isinstance(event.start, datetime)
    assert event.start.date() == date(2026, 3, 11)
    assert isinstance(event.status, sportindex.EventStatus)
    assert event.status.type == "finished"
    assert event.competition.id == "trnc:7"
    assert event.season.id == "trnc:7:trns:76953"
    assert event.venue.id == "vnu:843"
    assert event.score.home == 5 and event.score.away == 2
    assert event.winner.id == "team:1644"
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
    assert all(h2h_event.competitors.home.id == "team:1644" or h2h_event.competitors.away.id == "team:1644" for h2h_event in event.h2h)
    assert all(isinstance(channel, sportindex.Channel) for channel in event.get_channels("FR"))

    # Stage Event
    logger.info("Testing StageEvent...")
    event = Event.from_id("stg:214155", provider)
    assert isinstance(event, StageEvent)
    assert event.id == "stg:214155"
    assert event.name == "Japan GP"
    assert event.slug == "japan-gp"
    assert isinstance(event.start, datetime)
    assert isinstance(event.end, datetime)
    assert abs(event.end.date() - event.start.date()).days <= 4
    assert isinstance(event.status, sportindex.EventStatus)
    assert event.status.type == "finished"
    assert event.tier.name.lower() == "event"
    assert event.competition.id == "stgc:40"
    assert event.season.id == "stgc:40:stgs:214140"
    assert event.parent is None
    assert len(event.substages) > 0
    assert all(subevent.parent == event for subevent in event.substages)
    assert isinstance(event.venue, sportindex.Venue)
    assert isinstance(event.winner, sportindex.Competitor)
    assert all(isinstance(standings, sportindex.Standings) for standings in event.standings)
    assert all(isinstance(channel, sportindex.Channel) for channel in event.get_channels("FR"))
