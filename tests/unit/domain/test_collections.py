"""Collection semantics: uniqueness, querying, scoring and date handling.

Every grouped result the SDK returns is one of these, so their contracts are load-bearing.
"""

import pytest
from datetime import UTC, datetime

from sportindex.domain import (
    Competitor,
    EntityCollection,
    Event,
    EventCollection,
    MatchEvent,
    ScoredEntityCollection,
    StageEvent,
)

from factories import match, stage, team


class TestEntityCollectionUniqueness:
    def test_duplicates_are_dropped_on_construction(self, offline):
        a, b = Competitor(team(1), offline), Competitor(team(1), offline)
        assert len(EntityCollection([a, b])) == 1

    def test_insertion_order_is_preserved(self, offline):
        ids = ["t-cpt:3", "t-cpt:1", "t-cpt:2"]
        col = EntityCollection([Competitor(team(3), offline), Competitor(team(1), offline), Competitor(team(2), offline)])
        assert [e.id for e in col] == ids

    def test_add_ignores_an_entity_already_present(self, offline):
        col = EntityCollection([Competitor(team(1), offline)])
        col.add(Competitor(team(1), offline))
        col.add(Competitor(team(2), offline))
        assert [e.id for e in col] == ["t-cpt:1", "t-cpt:2"]

    def test_update_merges_and_keeps_first_occurrences(self, offline):
        col = EntityCollection([Competitor(team(1), offline)])
        col.update([Competitor(team(1), offline), Competitor(team(2), offline)])
        assert [e.id for e in col] == ["t-cpt:1", "t-cpt:2"]

    def test_non_entities_are_rejected(self):
        with pytest.raises(TypeError):
            EntityCollection(["not an entity"])

    @pytest.mark.parametrize("op", ["append", "extend", "insert"])
    def test_mutators_that_would_admit_duplicates_are_disabled(self, op, offline):
        col = EntityCollection([Competitor(team(1), offline)])
        with pytest.raises(NotImplementedError):
            getattr(col, op)(0, None) if op == "insert" else getattr(col, op)(Competitor(team(2), offline))

    def test_index_assignment_is_disabled(self, offline):
        col = EntityCollection([Competitor(team(1), offline)])
        with pytest.raises(NotImplementedError):
            col[0] = Competitor(team(2), offline)


class TestEntityCollectionQuerying:
    @pytest.fixture
    def squad(self, offline):
        return EntityCollection([
            Competitor(team(1, "Paris Saint-Germain"), offline),
            Competitor(team(2, "Olympique Marseille"), offline),
        ])

    def test_get_matches_on_any_attribute(self, squad):
        assert squad.get(name="Paris Saint-Germain").id == "t-cpt:1"
        assert squad.get(id="t-cpt:2").name == "Olympique Marseille"

    def test_get_returns_none_when_nothing_matches(self, squad):
        assert squad.get(name="Nobody") is None

    def test_get_strict_raises_when_nothing_matches(self, squad):
        from sportindex.exceptions import EntityNotFoundError
        with pytest.raises(EntityNotFoundError):
            squad.get(name="Nobody", strict=True)

    def test_search_is_a_case_insensitive_substring_match(self, squad):
        assert [e.id for e in squad.search("paris")] == ["t-cpt:1"]
        assert len(squad.search("olympique")) == 1
        assert len(squad.search("zzz")) == 0

    def test_set_operations_build_new_collections(self, offline):
        a = EntityCollection([Competitor(team(1), offline), Competitor(team(2), offline)])
        b = EntityCollection([Competitor(team(2), offline), Competitor(team(3), offline)])
        assert [e.id for e in a + b] == ["t-cpt:1", "t-cpt:2", "t-cpt:3"]
        assert [e.id for e in a | b] == ["t-cpt:1", "t-cpt:2", "t-cpt:3"]
        assert [e.id for e in a & b] == ["t-cpt:2"]
        assert len(a) == 2, "operands must not be mutated"


class TestScoredEntityCollection:
    @pytest.fixture
    def scored(self, offline):
        return ScoredEntityCollection([
            (Competitor(team(1), offline), 0.4),
            (Competitor(team(2), offline), 0.9),
        ])

    def test_scores_are_retrievable_by_id(self, scored):
        assert scored.get_score("t-cpt:2") == 0.9

    def test_an_unknown_id_is_rejected(self, scored):
        with pytest.raises(ValueError):
            scored.get_score("t-cpt:999")

    def test_the_highest_score_wins_for_a_repeated_entity(self, offline):
        col = ScoredEntityCollection([
            (Competitor(team(1), offline), 0.2),
            (Competitor(team(1), offline), 0.8),
        ])
        assert len(col) == 1
        assert col.get_score("t-cpt:1") == 0.8

    def test_sorting_is_best_first_by_default(self, scored):
        assert [e.id for e in scored.sort_by_score()] == ["t-cpt:2", "t-cpt:1"]
        assert [e.id for e in scored.sort_by_score(descending=False)] == ["t-cpt:1", "t-cpt:2"]

    def test_filtering_applies_the_bounds_given(self, scored):
        assert [e.id for e in scored.filter_by_score(min_score=0.5)] == ["t-cpt:2"]
        assert [e.id for e in scored.filter_by_score(max_score=0.5)] == ["t-cpt:1"]
        assert len(scored.filter_by_score()) == 2

    def test_slicing_keeps_the_scores(self, scored):
        top = scored.sort_by_score()[:1]
        assert isinstance(top, ScoredEntityCollection)
        assert top.get_score("t-cpt:2") == 0.9

    def test_to_collection_drops_scores_and_returns_a_mutable_collection(self, scored, offline):
        plain = scored.to_collection()
        assert type(plain) is EntityCollection
        plain.add(Competitor(team(3), offline))  # would raise on the scored collection

    def test_merge_keeps_the_highest_score_across_collections(self, offline):
        a = ScoredEntityCollection([(Competitor(team(1), offline), 0.3)])
        b = ScoredEntityCollection([(Competitor(team(1), offline), 0.7)])
        merged = ScoredEntityCollection.merge(a, b)
        assert len(merged) == 1
        assert merged.get_score("t-cpt:1") == 0.7

    @pytest.mark.parametrize("op,args", [
        ("add", (None,)), ("update", ([],)), ("search", ("x",)),
    ])
    def test_it_is_read_only(self, scored, op, args):
        with pytest.raises(NotImplementedError):
            getattr(scored, op)(*args)


class TestEventCollection:
    @pytest.fixture
    def mixed(self, offline):
        return EventCollection([
            Event(match(1, start=1_700_000_000), offline),
            Event(stage(2, start=1_600_000_000), offline),
            Event(stage(3, start=None), offline),
        ])

    def test_matches_and_stages_partition_the_collection(self, mixed):
        assert [e.id for e in mixed.matches] == ["mch:1"]
        assert [e.id for e in mixed.stages] == ["stg:2", "stg:3"]
        assert all(isinstance(e, MatchEvent) for e in mixed.matches)
        assert all(isinstance(e, StageEvent) for e in mixed.stages)

    def test_sorting_is_oldest_first_with_undated_events_last(self, mixed):
        assert [e.id for e in mixed.sort_by_date()] == ["stg:2", "mch:1", "stg:3"]

    def test_undated_events_stay_last_when_sorting_descending(self, mixed):
        assert [e.id for e in mixed.sort_by_date(ascending=False)] == ["mch:1", "stg:2", "stg:3"]

    def test_date_filters_drop_undated_events(self, mixed):
        after = mixed.filter_by_date(after=datetime(2000, 1, 1, tzinfo=UTC))
        assert [e.id for e in after] == ["mch:1", "stg:2"]

    def test_date_bounds_are_exclusive_and_independent(self, mixed):
        cutoff = datetime(2023, 1, 1, tzinfo=UTC)
        assert [e.id for e in mixed.filter_by_date(before=cutoff)] == ["stg:2"]
        assert [e.id for e in mixed.filter_by_date(after=cutoff)] == ["mch:1"]

    def test_a_bare_date_is_read_as_midnight(self, offline):
        from datetime import date
        col = EventCollection([Event(match(1, start=1_700_000_000), offline)])
        assert len(col.filter_by_date(after=date(2000, 1, 1))) == 1

    def test_filter_by_competitors_keeps_matches_with_either_side(self, offline):
        col = EventCollection([
            Event(match(1, home=team(10, "A"), away=team(20, "B")), offline),
            Event(match(2, home=team(30, "C"), away=team(40, "D")), offline),
        ])
        assert [e.id for e in col.filter_by_competitors(["t-cpt:40"])] == ["mch:2"]
        assert len(col.filter_by_competitors(["t-cpt:10", "t-cpt:30"])) == 2
        assert len(col.filter_by_competitors(["t-cpt:999"])) == 0

    def test_filter_by_competitors_never_returns_stage_events(self, mixed):
        # mch:1 is built from team(1) vs team(2), so this id does match a competitor —
        # the point is that the two StageEvents can never come back from this filter.
        result = mixed.filter_by_competitors(["t-cpt:1"])
        assert [e.id for e in result] == ["mch:1"]
        assert not any(isinstance(e, StageEvent) for e in result)
