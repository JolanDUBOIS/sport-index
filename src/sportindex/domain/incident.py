from typing import Annotated, Any

from pydantic import Field

from sportindex.provider.models import CardIncident as ProviderCard
from sportindex.provider.models import (
    ExtraTimeIncident,
    PeriodIncident,
    VarDecisionIncident,
    _ManagerData,
)
from sportindex.provider.models import GoalIncident as ProviderGoal
from sportindex.provider.models import Incident as ProviderIncident
from sportindex.provider.models import PenaltyIncident as ProviderPenalty
from sportindex.provider.models import (
    PenaltyShootoutIncident as ProviderPenaltyShootout,
)
from sportindex.provider.models import SubstitutionIncident as ProviderSubstitution

from .competitor import Competitor
from .manager import Manager


class GoalIncident(ProviderGoal):
    scorer: Competitor = Field(alias="player")
    assist: Competitor | None = None

class PenaltyIncident(ProviderPenalty):
    shooter: Competitor = Field(alias="player")

class PenaltyShootoutIncident(ProviderPenaltyShootout):
    shooter: Competitor = Field(alias="player")

class CardIncident(ProviderCard):
    recipient: Competitor | Manager

class SubstitutionIncident(ProviderSubstitution):
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
