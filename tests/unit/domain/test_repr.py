"""Rendering tests.

One implementation backs `__repr__` and `__str__` across the package, so these cover the
shared behaviour once and then check that each family — entities, collections, schemas and
the small domain models — is actually wired to it.
"""

from sportindex.domain import Category, EntityCollection, ScoredEntityCollection, Team
from sportindex.domain.base import DomainModel
from sportindex.domain.static import SPORTS_REGISTRY, SportEntry

from sportindex._repr import MISSING, ReprMixin  # isort: skip

from factories import category, team  # isort: skip


class _Plain(ReprMixin):
    _REPR_FIELDS = ("id", "name")

    def __init__(self, id=None, name=None):  # noqa: A002
        self.id = id
        self.name = name


class _NoFields(ReprMixin):
    pass


class TestSharedRendering:
    def test_repr_lists_declared_fields_under_the_concrete_class(self):
        assert repr(_Plain("x:1", "Thing")) == "<_Plain id='x:1', name='Thing'>"

    def test_str_is_the_display_name_alone(self):
        assert str(_Plain("x:1", "Thing")) == "Thing"

    def test_str_falls_back_to_repr_without_a_display_name(self):
        assert str(_NoFields()) == "<_NoFields>"

    def test_a_declared_field_the_instance_lacks_is_marked_missing(self):
        class _Partial(ReprMixin):
            _REPR_FIELDS = ("id", "absent")
            id = "x:1"

        assert MISSING in repr(_Partial())

    def test_a_nested_displayable_collapses_to_its_token(self):
        outer = _Plain("x:1", "Outer")
        outer.name = _Plain("y:2", "Inner")
        # The inner object contributes its token, not its own full repr.
        assert repr(outer) == "<_Plain id='x:1', name=<_Plain y:2>>"

    def test_a_token_without_an_id_names_the_class_alone(self):
        assert _NoFields()._repr_token() == "<_NoFields>"


class TestPydanticDerivedFields:
    def test_preferred_fields_are_used_when_declared(self):
        class _Schema(DomainModel):
            id: int
            name: str
            extra: str

        rendered = repr(_Schema(id=1, name="n", extra="e"))
        assert rendered == "<_Schema id=1, name='n'>"

    def test_falls_back_to_the_first_fields_when_none_are_preferred(self):
        class _Tally(DomainModel):
            yellow: int
            red: int

        assert repr(_Tally(yellow=3, red=1)) == "<_Tally yellow=3, red=1>"


class TestEntities:
    def test_entity_str_is_its_name(self, offline):
        assert str(Team(team(44, "PSG"), offline)) == "PSG"

    def test_entity_repr_names_its_fields(self, offline):
        rendered = repr(Team(team(44, "PSG"), offline))
        assert rendered.startswith("<Team id='team:44', name='PSG'")

    def test_entity_repr_bounds_a_nested_entity(self, offline):
        rendered = repr(Category(category(7, "France"), offline))
        # The nested Sport contributes a token rather than expanding in full.
        assert "sport=<Sport spt:1>" in rendered
        assert "name='Football'" not in rendered


class TestCollections:
    def test_empty_collection(self):
        assert repr(EntityCollection()) == "<EntityCollection empty>"

    def test_short_collection_lists_everything(self, offline):
        collection = EntityCollection([Team(team(i), offline) for i in (1, 2)])
        assert repr(collection) == "<EntityCollection 2 items: <Team team:1>, <Team team:2>>"

    def test_long_collection_previews_and_counts_the_rest(self, offline):
        collection = EntityCollection([Team(team(i), offline) for i in range(50)])
        rendered = repr(collection)
        assert rendered.startswith("<EntityCollection 50 items: <Team team:0>, ")
        assert rendered.endswith("+47 more>")
        # A summary, not a dump: bounded however many entities it holds.
        assert len(rendered) < 120

    def test_scored_collection_carries_its_scores(self, offline):
        collection = ScoredEntityCollection([(Team(team(1), offline), 0.75)])
        assert repr(collection) == "<ScoredEntityCollection 1 items: <Team team:1> (0.75)>"


class TestSchemas:
    def test_schema_repr_is_compact(self):
        rendered = repr(team(44, "PSG"))
        assert rendered == "<_TeamData id=44, name='PSG', slug='psg'>"

    def test_a_nested_schema_does_not_expand(self):
        # Pydantic's default would have dumped the whole nested sport and category models.
        assert "_SportData" not in repr(team(44, "PSG"))


class TestSportEntry:
    def test_named_tuple_matches_the_shared_format(self):
        entry = SportEntry(1, "football", "Football")
        assert repr(entry) == "<SportEntry id=1, slug='football', name='Football'>"
        assert str(entry) == "Football"

    def test_the_registry_renders(self):
        assert all(repr(entry).startswith("<SportEntry ") for entry in SPORTS_REGISTRY)


