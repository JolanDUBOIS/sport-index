"""SDK ID encoding, decoding and class resolution.

IDs are the SDK's public addressing scheme — every `client.get(...)` depends on them
round-tripping and on the prefix resolving to the right class.
"""

import pytest

from sportindex.domain import Competition, Competitor, Event, IdentifiableEntity, Season, Team

from factories import match, player, season, stage, team, tournament, unique_stage


class TestEncodeDecode:
    def test_a_plain_id_round_trips(self):
        encoded = Team.encode_id(44)
        assert encoded == "team:44"
        assert IdentifiableEntity.decode_id(encoded) == (None, "team", 44)

    def test_a_parent_id_is_prepended_when_given(self):
        assert Team.encode_id(44, parent_id="trnc:7") == "trnc:7:team:44"

    def test_a_nested_id_keeps_its_parent_intact(self):
        # A Season ID nests a Competition ID, so decoding must split from the right.
        parent, prefix, raw = IdentifiableEntity.decode_id("trnc:7:trns:61644")
        assert parent == "trnc:7"
        assert prefix == "trns"
        assert raw == 61644

    @pytest.mark.parametrize("bad", ["", "nocolon", "a:b:c:d:e"])
    def test_a_malformed_id_is_rejected(self, bad):
        with pytest.raises(ValueError):
            IdentifiableEntity.decode_id(bad)

    def test_a_non_numeric_raw_id_is_rejected(self):
        with pytest.raises(ValueError):
            IdentifiableEntity.decode_id("trnc:abc")


class TestResolveClass:
    @pytest.mark.parametrize("entity_id,expected", [
        ("mch:1", "MatchEvent"),
        ("stg:1", "StageEvent"),
        ("team:1", "Team"),
        ("vnu:1", "_StdVenue"),
        ("stgv:1", "_StageVenue"),
        ("trnc:1", "_TournamentCompetition"),
        ("stgc:1", "_StageCompetition"),
    ])
    def test_a_prefix_resolves_to_its_concrete_class(self, entity_id, expected):
        assert IdentifiableEntity.resolve_class(entity_id).__name__ == expected

    def test_an_unknown_prefix_is_rejected(self):
        with pytest.raises(ValueError, match="No subclass found globally"):
            IdentifiableEntity.resolve_class("nope:1")

    def test_resolving_from_the_wrong_base_says_which_class_owns_the_prefix(self):
        # Asking Competition to resolve an Event ID should name MatchEvent, not fail vaguely.
        with pytest.raises(ValueError, match="MatchEvent"):
            Competition.resolve_class("mch:1")


class TestIdsOnRealEntities:
    def test_entity_ids_carry_the_expected_prefix(self, offline):
        assert Competitor(team(44), offline).id == "team:44"
        assert Competitor(team(45, type=1), offline).id == "t-ath:45"
        assert Competitor(player(46), offline).id == "p-ath:46"
        assert Event(match(101), offline).id == "mch:101"
        assert Event(stage(202), offline).id == "stg:202"
        assert Competition(tournament(7), offline).id == "trnc:7"
        assert Competition(unique_stage(40), offline).id == "stgc:40"

    def test_a_season_id_nests_its_competition_id(self, offline):
        comp = Competition(tournament(7), offline)
        assert Season(season(61644), offline, competition=comp).id == "trnc:7:trns:61644"

    def test_equality_and_hashing_are_by_type_and_id(self, offline):
        a, b = Competitor(team(44), offline), Competitor(team(44), offline)
        assert a == b
        assert hash(a) == hash(b)
        assert a != Competitor(team(45), offline)

    def test_entities_of_different_types_never_compare_equal(self, offline):
        assert Event(match(1), offline) != Event(stage(1), offline)
