from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Any, TYPE_CHECKING

from .common import Amount
from .core import BaseModel, Sport, Country, Category
from .utils import timestamp_to_iso, iso_to_iso
if TYPE_CHECKING:
    from .tournament import UniqueTournament
    from .venue import Venue


# === Managers ===

@dataclass(frozen=True, kw_only=True)
class Performance(BaseModel):
    total: int
    wins: int
    draws: int
    losses: int
    goal_scored: int
    goal_conceded: int
    total_points: int

    @classmethod
    def _from_api(cls, raw: dict) -> Performance:
        return Performance(
            total=raw.get("total"),
            wins=raw.get("wins"),
            draws=raw.get("draws"),
            losses=raw.get("losses"),
            goal_scored=raw.get("goalScored"),
            goal_conceded=raw.get("goalConceded"),
            total_points=raw.get("totalPoints"),
        )

@dataclass(frozen=True, kw_only=True)
class Manager(BaseModel):
    id: str
    slug: str
    name: str
    short_name: str
    team: Team
    teams: list[Team]
    sport: Sport
    country: Country
    deceased: Optional[bool] = None
    date_of_birth: Optional[str] = None
    performance: Optional[Performance] = None
    preferred_formation: Optional[str] = None
    former_player_id: Optional[str] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Manager:
        return Manager(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            short_name=raw.get("shortName"),
            team=Team.from_api(raw.get("team")),
            teams=[Team.from_api(t) for t in raw.get("teams", [])],
            sport=Sport.from_api(raw.get("sport")),
            country=Country.from_api({**raw.get("country", {}), "alpha3": raw.get("nationality")}),
            deceased=raw.get("deceased"),
            date_of_birth=timestamp_to_iso(raw.get("dateOfBirthTimestamp"), kind="date"),
            performance=Performance.from_api(raw.get("performance")),
            preferred_formation=raw.get("preferredFormation"),
            former_player_id=raw.get("formerPlayerId"),
        )


# === Players ===

@dataclass(frozen=True, kw_only=True)
class Position(BaseModel):
    position: str
    primary: Optional[str] = None
    detailed: Optional[list[str]] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Position:
        return Position(
            position=raw.get("position"),
            primary=raw.get("primaryPosition"),
            detailed=raw.get("positionsDetailed"),
        )

@dataclass(frozen=True, kw_only=True)
class Player(BaseModel):
    id: str
    slug: str
    name: str
    short_name: str
    gender: str
    number: int
    team: Team
    position: Position
    country: Country
    weight: Optional[int] = None
    height: Optional[int] = None
    date_of_birth: Optional[str] = None
    status: Optional[str] = None
    retired: Optional[bool] = None
    deceased: Optional[bool] = None
    proposed_market_value: Optional[Amount] = None
    salary: Optional[Amount] = None
    handedness: Optional[str] = None
    preferred_foot: Optional[str] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Player:
        return Player(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            short_name=raw.get("shortName"),
            gender=raw.get("gender"),
            number=int(raw.get("shirtNumber")),
            team=Team.from_api(raw.get("team")),
            position=Position.from_api(raw),
            country=Country.from_api(raw.get("country")),
            weight=raw.get("weight"),
            height=raw.get("height"),
            date_of_birth=timestamp_to_iso(raw.get("dateOfBirthTimestamp"), kind="date"),
            status=raw.get("status"),
            retired=raw.get("retired"),
            deceased=raw.get("deceased"),
            proposed_market_value=Amount.from_api(raw.get("proposedMarketValueRaw")),
            salary=Amount.from_api(raw.get("salaryRaw")),
            handedness=raw.get("handedness"),
            preferred_foot=raw.get("preferredFoot"),
        )

@dataclass(frozen=True, kw_only=True)
class PlayerPreviousTeam(BaseModel):
    player: Player
    team: Team
    transfer_date: str

    @classmethod
    def _from_api(cls, raw: dict) -> PlayerPreviousTeam:
        return PlayerPreviousTeam(
            player=Player.from_api(raw.get("player")),
            team=Team.from_api(raw.get("previousTeam")),
            transfer_date=iso_to_iso(raw.get("transferDate"), kind="date")
        )

@dataclass(frozen=True, kw_only=True)
class TeamPlayers(BaseModel):
    players: list[Player]
    foreign_players: list[Player]
    national_players: list[Player]
    player_previous_teams: list[PlayerPreviousTeam]

    @classmethod
    def _from_api(cls, raw: dict) -> TeamPlayers:
        return TeamPlayers(
            players=[Player.from_api(player) for player in raw.get("players", [])],
            foreign_players=[Player.from_api(player) for player in raw.get("foreignPlayers", [])],
            national_players=[Player.from_api(player) for player in raw.get("nationalPlayers", [])],
            player_previous_teams=[PlayerPreviousTeam.from_api(ppt) for ppt in raw.get("playerPreviousTeams", [])],
        )


# === Referees ===

@dataclass(frozen=True, kw_only=True)
class Cards(BaseModel):
    yellow: int
    red: int
    yellow_red: int

    @classmethod
    def _from_api(cls, raw: dict) -> Cards:
        return Cards(
            yellow=raw.get("yellowCards"),
            red=raw.get("redCards"),
            yellow_red=raw.get("yellowRedCards"),
        )

@dataclass(frozen=True, kw_only=True)
class Referee(BaseModel):
    id: str
    slug: str
    name: str
    games: int
    sport: Sport
    country: Country
    cards: Optional[Cards] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Referee:
        return Referee(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            games=raw.get("games"),
            sport=Sport.from_api(raw.get("sport")),
            country=Country.from_api(raw.get("country")),
            cards=Cards.from_api(raw) if any(key in raw for key in ["yellowCards", "redCards", "yellowRedCards"]) else None,
        )


# === Teams ===

@dataclass(frozen=True, kw_only=True)
class PlayerTeamInfo(BaseModel): # When a team is a player for an individual sport (e.g. tennis)
    id: str
    residence: Optional[str] = None
    birth_place: Optional[str] = None
    height: Optional[float] = None # in m
    weight: Optional[float] = None # in kg
    handedness: Optional[str] = None # e.g. "right-handed", "left-handed"...
    prize_current: Optional[Amount] = None
    prize_total: Optional[Amount] = None
    date_of_birth: Optional[str] = None
    current_ranking: Optional[int] = None

    @classmethod
    def _from_api(cls, raw: dict) -> PlayerTeamInfo:
        return PlayerTeamInfo(
            id=raw.get("id"),
            residence=raw.get("residence"),
            birth_place=raw.get("birthplace"),
            height=raw.get("height"),
            weight=raw.get("weight"),
            handedness=raw.get("handedness"),
            prize_current=Amount.from_api(raw.get("prizeCurrentRaw")),
            prize_total=Amount.from_api(raw.get("prizeTotalRaw")),
            date_of_birth=timestamp_to_iso(raw.get("birthDateTimestamp"), kind="date"),
            current_ranking=raw.get("currentRanking"),
        )


@dataclass(frozen=True, kw_only=True)
class Team(BaseModel):
    id: str
    slug: str
    name: str
    short_name: str
    full_name: str
    name_code: str
    national: bool
    disabled: bool
    gender: str
    country: Country
    sport: Sport
    category: Optional[Category] = None
    primary_unique_tournament: Optional[UniqueTournament] = None
    manager: Optional[Manager] = None
    parent: Optional[Team] = None
    venue: Optional[Venue] = None
    ranking: Optional[int] = None
    founded: Optional[str] = None
    player_team_info: Optional[PlayerTeamInfo] = None

    @classmethod
    def _from_api(cls, raw: dict) -> Team:
        from .tournament import UniqueTournament # Avoid circular imports
        from .venue import Venue # Avoid circular imports
        return Team(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            short_name=raw.get("shortName"),
            full_name=raw.get("fullName"),
            name_code=raw.get("nameCode"),
            national=raw.get("national"),
            disabled=raw.get("disabled"),
            gender=raw.get("gender"),
            country=Country.from_api(raw.get("country")),
            sport=Sport.from_api(raw.get("sport")),
            category=Category.from_api(raw.get("category")),
            primary_unique_tournament=UniqueTournament.from_api(raw.get("primaryUniqueTournament")),
            manager=Manager.from_api(raw.get("manager")),
            parent=Team.from_api(raw.get("parentTeam")),
            venue=Venue.from_api(raw.get("venue")),
            ranking=raw.get("ranking"),
            founded=timestamp_to_iso(raw.get("foundationDateTimestamp"), kind="date"),
            player_team_info=PlayerTeamInfo.from_api(raw.get("playerTeamInfo", {})),
        )

# Note - Additional keys:
# - wdlRecords (MMA)


# === Team Season Statistics ===

_TEAM_SEASON_STATS_META_KEYS = {"id", "statisticsType"}

@dataclass(frozen=True, kw_only=True)
class TeamSeasonStats(BaseModel):
    id: str
    sport: str
    stats: dict[str, Any]

    @classmethod
    def _from_api(cls, raw: dict) -> TeamSeasonStats:
        inner = raw.get("statistics", raw)
        return TeamSeasonStats(
            id=inner.get("id"),
            sport=inner.get("statisticsType", {}).get("sportSlug"),
            stats={k: v for k, v in inner.items() if k not in _TEAM_SEASON_STATS_META_KEYS},
        )
