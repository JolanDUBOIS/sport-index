"""When a match fetches its full record.

Event lists already carry a match's tournament and season, and a competition's list carries
its venue too. Reading those must not cost a request per match; only data the list lacks
justifies fetching the full event.
"""

from __future__ import annotations

from factories import match, season, tournament, venue

from sportindex.api_client.models import _TournamentData
from sportindex.domain import MatchEvent

TOURNAMENT = _TournamentData(id=1, slug="premier-league", name="Premier League",
                             unique_tournament=tournament(17, "Premier League"))
LISTED = {"tournament": TOURNAMENT.model_dump(by_alias=True),
          "season": season(76986, "Premier League 25/26").model_dump(by_alias=True)}


class CountingProvider:
    """Serves the full event, counting how often it is asked for."""

    def __init__(self) -> None:
        self.event_requests = 0

    def get_event(self, event_id: int):
        self.event_requests += 1
        return match(event_id, venue=venue(1, "MKM Stadium").model_dump(by_alias=True), **LISTED)


def test_a_competition_list_event_answers_from_its_payload(offline):
    event = MatchEvent(match(16363634, venue=venue(1, "MKM Stadium").model_dump(by_alias=True), **LISTED), offline)

    assert event.competition.name == "Premier League"
    assert event.season is not None
    assert event.venue.name == "MKM Stadium"


def test_a_team_list_event_fetches_only_its_missing_venue():
    provider = CountingProvider()
    event = MatchEvent(match(16363634, **LISTED), provider)

    assert event.competition.name == "Premier League"
    assert provider.event_requests == 0
    assert event.venue.name == "MKM Stadium"
    assert event.venue.name == "MKM Stadium"
    assert provider.event_requests == 1
