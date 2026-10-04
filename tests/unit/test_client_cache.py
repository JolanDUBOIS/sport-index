"""Cache namespacing on SportClient.

An entity must land in one namespace regardless of how it was requested — otherwise the
cache misses, and no public namespace name can clear it. Private dispatch variants must never
surface as namespace names.
"""

import pytest

from sportindex import (
    Athlete,
    Category,
    Channel,
    Competition,
    Competitor,
    Event,
    MatchEvent,
    Season,
    Sport,
    SportClient,
    StageEvent,
    Team,
    Venue,
)
from sportindex.domain import IdentifiableEntity


@pytest.fixture
def cache_client() -> SportClient:
    """A real cache_client. Constructing one performs no I/O, and these tests never fetch.

    Deliberately not named `client` — that fixture name marks a test as integration.
    """
    return SportClient()


class TestNamespaceResolution:
    @pytest.mark.parametrize("cls,expected", [
        (Sport, "sport"), (Category, "category"), (Channel, "channel"),
        (Competition, "competition"), (Season, "season"), (Venue, "venue"),
        (Event, "event"), (MatchEvent, "event"), (StageEvent, "event"),
        (Competitor, "competitor"), (Team, "competitor"), (Athlete, "competitor"),
    ])
    def test_public_classes_map_to_their_own_namespace(self, cache_client, cls, expected):
        assert cache_client._resolve_ns(cls) == expected

    @pytest.mark.parametrize("entity_id,expected", [
        ("vnu:1", "venue"), ("stgv:1", "venue"),
        ("trnc:1", "competition"), ("stgc:1", "competition"),
        ("team:1", "competitor"), ("t-ath:1", "competitor"), ("p-ath:1", "competitor"),
        ("mch:1", "event"), ("stg:1", "event"),
    ])
    def test_a_class_inferred_from_an_id_lands_in_the_public_namespace(self, cache_client, entity_id, expected):
        """get('vnu:1') and get('vnu:1', Venue) must share a namespace, or the cache misses."""
        inferred = IdentifiableEntity.resolve_class(entity_id)
        assert cache_client._resolve_ns(inferred) == expected

    def test_no_namespace_is_ever_a_private_class_name(self, cache_client):
        for entity_id in ("vnu:1", "stgv:1", "trnc:1", "stgc:1", "team:1", "t-ath:1", "p-ath:1"):
            ns = cache_client._resolve_ns(IdentifiableEntity.resolve_class(entity_id))
            assert not ns.startswith("_")
            assert ns in SportClient.CACHE_NAMESPACES


class TestClearCache:
    def test_clearing_an_empty_but_valid_namespace_is_a_no_op(self, cache_client):
        for ns in SportClient.CACHE_NAMESPACES:
            cache_client.clear_cache(ns)  # must not raise on a fresh client

    def test_an_unknown_namespace_is_still_rejected(self, cache_client):
        with pytest.raises(KeyError, match="Unknown cache namespace"):
            cache_client.clear_cache("events")  # plural is a typo

    def test_it_is_case_insensitive(self, cache_client):
        cache_client.clear_cache("EVENT")

    def test_clearing_one_namespace_leaves_the_others(self, cache_client):
        cache_client._cache["venue"]["vnu:1"] = object()
        cache_client._cache["competition"]["trnc:1"] = object()
        cache_client.clear_cache("venue")
        assert not cache_client._cache.get("venue")
        assert len(cache_client._cache["competition"]) == 1

    def test_clearing_everything_empties_all_namespaces(self, cache_client):
        cache_client._cache["venue"]["vnu:1"] = object()
        cache_client._cache["competition"]["trnc:1"] = object()
        cache_client.clear_cache()
        assert not any(cache_client._cache.values())

    def test_every_resolvable_namespace_is_declared(self, cache_client):
        """CACHE_NAMESPACES must stay in step with what _resolve_ns can produce."""
        produced = {
            cache_client._resolve_ns(cls)
            for cls in (Sport, Category, Channel, Competition, Season, Venue,
                        Event, MatchEvent, StageEvent, Competitor, Team, Athlete)
        }
        assert produced <= SportClient.CACHE_NAMESPACES
