"""Variant dispatch: constructing a public class yields the right private subclass.

Users only ever name the public class. These tests pin the mapping from payload shape to
variant, and confirm the private classes stay an implementation detail.
"""

import pytest

from sportindex.domain import (
    Athlete,
    Competition,
    Competitor,
    Event,
    MatchEvent,
    Season,
    StageEvent,
    Team,
    Venue,
)

from factories import (
    manager,
    match,
    player,
    season,
    stage,
    team,
    tournament,
    unique_stage,
    venue,
)


class TestVariantSelection:
    def test_competitor_is_built_as_a_team_or_an_athlete(self, offline):
        assert type(Competitor(team(1, type=0), offline)) is Team
        assert type(Competitor(team(1, type=1), offline)).__name__ == "_TeamAthlete"
        assert type(Competitor(team(1, type=2), offline)) is Team  # a doubles pair
        assert type(Competitor(player(1), offline)).__name__ == "_PlayerAthlete"

    def test_type_wins_over_athlete_details(self, offline):
        # Tyrrell, an F1 team, carries a playerTeamInfo block.
        tyrrell = team(513376, "Tyrrell", type=0, player_team_info={"id": 1})
        assert type(Competitor(tyrrell, offline)) is Team

    def test_without_type_athlete_details_decide(self, offline):
        assert type(Competitor(team(1), offline)) is Team
        assert type(Competitor(team(1, player_team_info={"id": 1}), offline)).__name__ == "_TeamAthlete"

    def test_event_dispatches_to_its_two_public_kinds(self, offline):
        assert isinstance(Event(match(1), offline), MatchEvent)
        assert isinstance(Event(stage(1), offline), StageEvent)

    def test_competition_dispatches_on_payload_shape(self, offline):
        assert type(Competition(tournament(), offline)).__name__ == "_TournamentCompetition"
        assert type(Competition(unique_stage(), offline)).__name__ == "_StageCompetition"

    def test_venue_dispatches_on_payload_shape(self, offline):
        assert type(Venue(venue(1), offline)).__name__ == "_StdVenue"
        assert type(Venue(stage(1), offline)).__name__ == "_StageVenue"

    def test_season_dispatches_on_payload_shape(self, offline):
        comp = Competition(tournament(), offline)
        assert type(Season(season(), offline, competition=comp)).__name__ == "_TournamentSeason"
        from sportindex.api_client.models import StageTier
        assert type(Season(stage(1, tier=StageTier.SEASON), offline)).__name__ == "_StageSeason"

    def test_athlete_dispatches_on_payload_shape(self, offline):
        assert type(Athlete(player(1), offline)).__name__ == "_PlayerAthlete"
        squad_member = team(1, player_team_info={"id": 1})
        assert type(Athlete(squad_member, offline)).__name__ == "_TeamAthlete"


class TestVariantsStayHidden:
    def test_variants_are_not_exported(self):
        import sportindex
        import sportindex.domain as domain
        for hidden in ("_TeamCompetitor", "_PlayerCompetitor", "_TournamentSeason",
                       "_StageSeason", "_TournamentCompetition", "_StageCompetition",
                       "_StdVenue", "_StageVenue", "_TeamAthlete", "_PlayerAthlete"):
            assert hidden not in domain.__all__
            assert hidden not in sportindex.__all__

    def test_a_variant_names_no_class_in_str(self, offline):
        # __str__ is the display name alone, so no class name reaches it at all; __repr__
        # keeps the concrete class, which is the one worth seeing while debugging dispatch.
        athlete = Competitor(team(44, "Aryna Sabalenka", type=1), offline)
        assert str(athlete) == "Aryna Sabalenka"
        assert repr(athlete).startswith("<_TeamAthlete ")

    def test_isinstance_against_the_public_class_holds(self, offline):
        assert isinstance(Competitor(team(1), offline), Competitor)
        assert isinstance(Competition(tournament(), offline), Competition)
        assert isinstance(Venue(venue(1), offline), Venue)


class TestResolve:
    def test_a_team_payload_without_player_info_is_not_an_athlete(self, offline):
        assert isinstance(Team(team(1), offline).resolve(), Team)

    def test_a_player_competitor_resolves_to_an_athlete(self, offline):
        resolved = Competitor(player(1), offline).resolve()
        assert isinstance(resolved, Athlete)

    def test_resolve_is_idempotent(self, offline):
        competitor = Competitor(player(1), offline)
        assert competitor.resolve() is competitor.resolve()


class TestRejectedPayloads:
    @pytest.mark.parametrize("cls,bad", [
        (Competitor, "nonsense"),
        (Event, "nonsense"),
        (Competition, "nonsense"),
        (Venue, "nonsense"),
        (Season, "nonsense"),
    ])
    def test_an_unrecognised_payload_is_rejected(self, cls, bad, offline):
        with pytest.raises(TypeError):
            cls(bad, offline)

    def test_a_manager_payload_is_not_a_competitor(self, offline):
        with pytest.raises(TypeError):
            Competitor(manager(1), offline)

    def test_a_stage_below_season_tier_cannot_be_a_season(self, offline):
        from sportindex.api_client.models import StageTier
        with pytest.raises(ValueError, match="tier SEASON"):
            Season(stage(1, tier=StageTier.RACE), offline)

    def test_a_season_tier_stage_cannot_be_an_event(self, offline):
        from sportindex.api_client.models import StageTier
        with pytest.raises(ValueError, match="EVENT or below"):
            Event(stage(1, tier=StageTier.SEASON), offline)

    def test_a_match_based_season_needs_its_competition(self, offline):
        from sportindex.exceptions import InsufficientDataError
        with pytest.raises(InsufficientDataError):
            Season(season(), offline)
