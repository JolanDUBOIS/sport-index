from typing import Annotated, Any

from pydantic import Field

from sportindex.api_client.models import CardIncident as ProviderCard
from sportindex.api_client.models import (
    ExtraTimeIncident,
    PeriodIncident,
    VarDecisionIncident,
    _ManagerData,
)
from sportindex.api_client.models import GoalIncident as ProviderGoal
from sportindex.api_client.models import Incident as ProviderIncident
from sportindex.api_client.models import PenaltyIncident as ProviderPenalty
from sportindex.api_client.models import (
    PenaltyShootoutIncident as ProviderPenaltyShootout,
)
from sportindex.api_client.models import SubstitutionIncident as ProviderSubstitution

from .competitor import Competitor
from .manager import Manager


class GoalIncident(ProviderGoal):
    """A goal, try or equivalent score, with the running score it produced.

    Attributes:
        scorer (Competitor): Who scored.
        assist (Competitor | None): Who assisted, if anyone.
        score (Score): The score immediately after this goal.
        side (str): Which side scored — "home" or "away".
        time (int): Minute of the goal; -1 when the provider gives no time.
        extra_time (int | None): Minutes into added time, if the goal came in it.
        kind (str): What sort of goal, e.g. "regular", "ownGoal", "penalty".
        id (int): The provider's raw incident ID.
    """
    scorer: Competitor = Field(alias="player")
    assist: Competitor | None = None

class PenaltyIncident(ProviderPenalty):
    """A penalty taken during normal play.

    Attributes:
        shooter (Competitor): Who took it.
        side (str): Which side took it — "home" or "away".
        time (int): Minute of the penalty; -1 when the provider gives no time.
        extra_time (int | None): Minutes into added time, if it came in it.
        description (str | None): The provider's free-text note, if any.
        kind (str): The outcome, e.g. "missed".
        id (int): The provider's raw incident ID.
    """
    shooter: Competitor = Field(alias="player")

class PenaltyShootoutIncident(ProviderPenaltyShootout):
    """One penalty in a shootout, with the running shootout score.

    Attributes:
        shooter (Competitor): Who took it.
        score (Score): The shootout score immediately after this kick.
        side (str): Which side took it — "home" or "away".
        kind (str): The outcome — "scored" or "missed".
        id (int): The provider's raw incident ID.
    """
    shooter: Competitor = Field(alias="player")

class CardIncident(ProviderCard):
    """A card shown to a player or to a member of the coaching staff.

    Attributes:
        recipient (Competitor | Manager): Who was booked — a player, or the manager.
        side (str): Which side was booked — "home" or "away".
        time (int): Minute of the card; -5 means it was shown on the bench.
        extra_time (int | None): Minutes into added time, if it came in it.
        reason (str | None): Why it was shown, if the provider states it.
        rescinded (bool): Whether the card was later withdrawn.
        kind (str): Which card — "yellow", "red" or "yellowRed".
        id (int): The provider's raw incident ID.
    """
    recipient: Competitor | Manager

class SubstitutionIncident(ProviderSubstitution):
    """A substitution.

    Attributes:
        player_in (Competitor): Who came on.
        player_out (Competitor): Who went off.
        side (str): Which side substituted — "home" or "away".
        time (int): Minute of the change.
        extra_time (int | None): Minutes into added time, if it came in it.
        kind (str): Why the change was made, e.g. "regular", "injury".
        id (int): The provider's raw incident ID.
    """
    player_in: Competitor = Field(alias="playerIn")
    player_out: Competitor = Field(alias="playerOut")


Incident = Annotated[
    GoalIncident
    | PenaltyIncident
    | PenaltyShootoutIncident
    | CardIncident
    | PeriodIncident
    | VarDecisionIncident
    | SubstitutionIncident
    | ExtraTimeIncident,
    Field(discriminator="incident_type")
]


def to_domain_incident(raw: ProviderIncident, provider: Any) -> Incident:
    if isinstance(raw, ProviderGoal):
        return GoalIncident(
            **raw.model_dump(by_alias=True, exclude={"scorer", "assist"}),
            scorer=Competitor(raw.scorer, provider),
            assist=Competitor(raw.assist, provider) if raw.assist else None
        )

    if isinstance(raw, (ProviderPenalty, ProviderPenaltyShootout)):
        domain_class = PenaltyIncident if isinstance(raw, ProviderPenalty) else PenaltyShootoutIncident
        return domain_class(
            **raw.model_dump(by_alias=True, exclude={"shooter"}),
            shooter=Competitor(raw.shooter, provider)
        )

    if isinstance(raw, ProviderCard):
        recipient = (
            Manager(raw.recipient, provider)
            if isinstance(raw.recipient, _ManagerData)
            else Competitor(raw.recipient, provider)
        )
        return CardIncident(
            **raw.model_dump(by_alias=True, exclude={"recipient"}),
            recipient=recipient
        )

    if isinstance(raw, ProviderSubstitution):
        return SubstitutionIncident(
            **raw.model_dump(by_alias=True, exclude={"player_in", "player_out"}),
            player_in=Competitor(raw.player_in, provider),
            player_out=Competitor(raw.player_out, provider)
        )

    return raw
