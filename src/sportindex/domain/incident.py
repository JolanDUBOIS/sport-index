from typing import Annotated, Any

from pydantic import Field

from .competitor import Competitor
from .manager import Manager
from sportindex.provider.models import (
    Incident as ProviderIncident,
    GoalIncident as ProviderGoal,
    PenaltyIncident as ProviderPenalty,
    PenaltyShootoutIncident as ProviderPenaltyShootout,
    CardIncident as ProviderCard,
    SubstitutionIncident as ProviderSubstitution,
    PeriodIncident,
    VarDecisionIncident,
    ExtraTimeIncident,
    _ManagerData
)


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
    
    if isinstance(raw, ProviderPenalty) or isinstance(raw, ProviderPenaltyShootout):
        DomainClass = PenaltyIncident if isinstance(raw, ProviderPenalty) else PenaltyShootoutIncident
        return DomainClass(
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
