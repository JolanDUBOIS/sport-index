"""
Participant domain entities: Competitor, Manager, Referee.

Competitor is the unified entity for both teams and individual athletes.
The discriminant is `kind` ("team" or "player"), set explicitly via
`_from_raw_team()` / `_from_raw_player()` constructors.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Literal, TYPE_CHECKING

from .base import BaseEntity, _normalize_dt
from .values import Amount, _amount_from_raw, Cards, _cards_from_raw, Performance, _performance_from_raw
from ..provider.parsers import timestamp_to_dt

if TYPE_CHECKING:
    from .competition import Competition
    from .core import Sport, Country, Category
    from .event import Event
    from .season import Season
    from .venue import Venue

logger = logging.getLogger(__name__)


# =====================================================================
# Competitor (team or individual athlete)
# =====================================================================

class Competitor(BaseEntity):
    """A team or individual athlete.

    Always constructed via `_from_raw_team()` or `_from_raw_player()` — never
    the bare __init__. The `kind` property tells you which one it is.
    """

    def __init__(
        self,
        *,
        id: int,
        slug: str,
        name: str,
        short_name: Optional[str] = None,
        full_name: Optional[str] = None,
        name_code: Optional[str] = None,
        gender: Optional[Literal["M", "F", "X"]] = None,
        national: bool = False,
    ) -> None:
        super().__init__()
        self.id = id
        self.slug = slug
        self.name = name
        self._source: Literal["raw_team", "raw_player"] = "raw_team"  # set by classmethods
        self._kind: Literal["team", "player"] | None = None
        self.short_name = short_name
        self.full_name = full_name
        self.name_code = name_code
        self.gender = gender
        self.national = national

        # Lazy-loaded relations
        self._sport: Optional[Sport] = None
        self._country: Optional[Country] = None
        self._category: Optional[Category] = None
        self._parent: Optional[Competitor] = None
        self._manager: Optional[Manager] = None
        self._players: Optional[list[Competitor]] = None
        self._venue: Optional[Venue] = None
        self._details: Optional[TeamDetails | PlayerDetails] = None
        self._seasons: Optional[list[Season]] = None

    # -- Constructors -------------------------------------------------- #

    @classmethod
    def _from_raw_team(cls, raw: dict) -> Competitor:
        """Build a Competitor from a RawTeam dict."""
        comp = cls(
            id=raw.get("id", 0),
            slug=raw.get("slug", ""),
            name=raw.get("name", ""),
            short_name=raw.get("shortName"),
            full_name=raw.get("fullName"),
            name_code=raw.get("nameCode"),
            gender=raw.get("gender"),
            national=raw.get("national", False),
        )
        comp._source = "raw_team"
        comp._raw = raw

        # Eagerly resolve sport/country if available
        from .core import Sport, Country
        if "sport" in raw and raw["sport"]:
            comp._sport = Sport._from_raw(raw["sport"])
        if "country" in raw and raw["country"]:
            comp._country = Country._from_raw(raw["country"])

        return comp

    @classmethod
    def _from_raw_player(cls, raw: dict) -> Competitor:
        """Build a Competitor from a RawPlayer dict."""
        comp = cls(
            id=raw.get("id", 0),
            slug=raw.get("slug", ""),
            name=raw.get("name", ""),
            short_name=raw.get("shortName"),
            gender=raw.get("gender"),
        )
        comp._source = "raw_player"
        comp._kind = "player"  # always certain for player-sourced
        comp._raw = raw

        from .core import Country
        if "country" in raw and raw["country"]:
            comp._country = Country._from_raw(raw["country"])

        return comp

    # -- Properties ---------------------------------------------------- #

    @property
    def kind(self) -> Literal["team", "player"]:
        """Whether this competitor is a team or an individual player.

        When built from ``_from_raw_team()``, kind is unresolved until
        ``_load_full()`` fetches the full data and checks for
        ``playerTeamInfo``.
        """
        if self._kind is not None:
            return self._kind
        self._load_full()
        if "playerTeamInfo" in self._raw and self._raw["playerTeamInfo"]:
            self._kind = "player"
        else:
            self._kind = "team"
        return self._kind

    @property
    def sport(self) -> Optional[Sport]:
        if self._sport is None:
            from .core import Sport
            raw_sport = self._raw.get("sport")
            if not raw_sport:
                self._load_full()
                raw_sport = self._raw.get("sport")
            if raw_sport:
                self._sport = Sport._from_raw(raw_sport)
        return self._sport

    @property
    def country(self) -> Optional[Country]:
        if self._country is None:
            from .core import Country
            raw_country = self._raw.get("country")
            if not raw_country:
                self._load_full()
                raw_country = self._raw.get("country")
            if raw_country:
                self._country = Country._from_raw(raw_country)
        return self._country

    @property
    def parent(self) -> Optional[Competitor]:
        """For players: parent team. For B-teams: A-team. None otherwise."""
        if self._parent is not None:
            return self._parent
        self._load_full()

        if self.kind == "player":
            # Player from RawPlayer → team key; player from RawTeam → parentTeam key
            raw_parent = self._raw.get("team") or self._raw.get("parentTeam")
            if raw_parent:
                self._parent = Competitor._from_raw_team(raw_parent)
        elif self.kind == "team":
            raw_parent = self._raw.get("parentTeam")
            if raw_parent:
                self._parent = Competitor._from_raw_team(raw_parent)

        return self._parent

    @property
    def manager(self) -> Optional[Manager]:
        """The current manager/coach (teams only)."""
        if self._manager is not None:
            return self._manager
        if self.kind != "team":
            return None
        self._load_full()
        if "manager" in self._raw and self._raw["manager"]:
            self._manager = Manager._from_raw(self._raw["manager"])
        return self._manager

    @property
    def players(self) -> Optional[list[Competitor]]:
        """Fetch squad / roster (teams only, lazy)."""
        if self._players is not None:
            return self._players
        if self.kind != "team":
            return None

        logger.debug("Fetching players for team '%s' (id=%s)", self.name, self.id)
        response = self._provider.get_team_players(str(self.id))
        raw_players = response.get("players", [])
        self._players = [
            Competitor._from_raw_player(p)
            for p in raw_players
        ]
        return self._players

    @property
    def venue(self) -> Optional[Venue]:
        """Home venue (teams only)."""
        if self._venue is not None:
            return self._venue
        if self.kind != "team":
            return None
        self._load_full()
        from .venue import Venue
        self._venue = Venue._from_raw(self._raw.get("venue"))
        return self._venue

    @property
    def details(self) -> Optional[TeamDetails | PlayerDetails]:
        """Extended details — shape depends on `kind`."""
        if self._details is not None:
            return self._details
        self._load_full()

        if self.kind == "team":
            from .competition import Competition

            primary_comp = None
            if self._raw.get("primaryUniqueTournament"):
                primary_comp = Competition._from_raw_unique_tournament(
                    self._raw["primaryUniqueTournament"]
                )

            self._details = TeamDetails(
                disabled=self._raw.get("disabled"),
                founded=timestamp_to_dt(self._raw.get("foundationDateTimestamp"), kind="date"),
                primary_competition=primary_comp,
            )

        elif self.kind == "player":
            # Player data can come from RawPlayer or RawTeam (with playerTeamInfo)
            pti = self._raw.get("playerTeamInfo", {})

            if pti:
                # This is a solo-sport athlete wrapped in a team
                self._details = PlayerDetails(
                    number=None,
                    position=None,
                    weight=pti.get("weight"),
                    height=pti.get("height"),
                    birth_place=pti.get("birthplace"),
                    birth_date=timestamp_to_dt(pti.get("birthDateTimestamp"), kind="date"),
                    retired=None,
                    deceased=None,
                    market_value=None,
                    salary=None,
                    handedness=pti.get("handedness"),
                    preferred_foot=None,
                    current_earnings=_amount_from_raw(pti.get("prizeCurrentRaw")),
                    career_earnings=_amount_from_raw(pti.get("prizeTotalRaw")),
                    ranking=pti.get("currentRanking"),
                )
            else:
                # Standard player from RawPlayer
                self._details = PlayerDetails(
                    number=self._raw.get("shirtNumber"),
                    position=self._raw.get("position"),
                    weight=self._raw.get("weight"),
                    height=self._raw.get("height"),
                    birth_place=None,
                    birth_date=timestamp_to_dt(self._raw.get("dateOfBirthTimestamp"), kind="date"),
                    retired=self._raw.get("retired"),
                    deceased=self._raw.get("deceased"),
                    market_value=_amount_from_raw(self._raw.get("proposedMarketValueRaw")),
                    salary=_amount_from_raw(self._raw.get("salaryRaw")),
                    handedness=self._raw.get("handedness"),
                    preferred_foot=self._raw.get("preferredFoot"),
                    current_earnings=None,
                    career_earnings=None,
                    ranking=None,
                )

        return self._details

    @property
    def seasons(self) -> list[Season]:
        """Fetch seasons this competitor has participated in (lazy)."""
        if self._seasons is not None:
            return self._seasons

        from .season import Season
        from .competition import Competition

        logger.debug("Fetching seasons for competitor '%s' (id=%s)", self.name, self.id)
        raw_uts_seasons = self._provider.get_team_seasons(str(self.id))
        self._seasons = []
        for uts in raw_uts_seasons:
            comp = None
            if "uniqueTournament" in uts and uts["uniqueTournament"]:
                comp = Competition._from_raw_unique_tournament(uts["uniqueTournament"])
            for raw_season in uts.get("seasons", []):
                self._seasons.append(
                    Season._from_raw_season_tournament(raw_season, competition=comp)
                )
        return self._seasons

    def events(
        self,
        *,
        max_events: int | None = None,
        before: date | datetime | None = None,
        after: date | datetime | None = None,
    ) -> list[Event]:
        """Fetch all events for this competitor.

        For teams, merges results and fixtures (two paginated endpoints).
        For players, only results are available.

        Args:
            max_events: Stop after collecting this many events.
            before: Only events starting strictly before this date/datetime.
            after:  Only events starting strictly after this date/datetime.
        """
        before_dt = _normalize_dt(before)
        after_dt = _normalize_dt(after)
        cid = str(self.id)

        if self._source == "raw_player":
            logger.debug("Fetching events for player '%s' (id=%s)", self.name, self.id)
            return self._fetch_event_pages(
                lambda p: self._provider.get_player_results(cid, page=p),
                max_events=max_events,
                before=before_dt,
                after=after_dt,
                ascending=False,
            )

        logger.debug("Fetching all events for team '%s' (id=%s)", self.name, self.id)
        past = self._fetch_event_pages(
            lambda p: self._provider.get_team_results(cid, page=p),
            before=before_dt,
            after=after_dt,
            ascending=False,
        )
        future = self._fetch_event_pages(
            lambda p: self._provider.get_team_fixtures(cid, page=p),
            before=before_dt,
            after=after_dt,
            ascending=True,
        )
        all_events = past + future
        all_events.sort(key=lambda e: e.start or datetime.min)
        if max_events is not None:
            all_events = all_events[:max_events]
        return all_events

    def fixtures(
        self,
        *,
        max_events: int | None = None,
        before: date | datetime | None = None,
        after: date | datetime | None = None,
    ) -> list[Event]:
        """Fetch upcoming fixtures for this competitor.

        Only available for teams — players have no fixtures endpoint.
        Defaults to events starting after *now*.

        Args:
            max_events: Stop after collecting this many events.
            before: Only events starting strictly before this date/datetime.
            after:  Only events starting strictly after this date/datetime.
                    Defaults to now.
        """
        if self._source == "raw_player":
            logger.info("No fixtures endpoint for players — returning empty list")
            return []

        if after is None:
            after = datetime.now()

        cid = str(self.id)
        logger.debug("Fetching fixtures for team '%s' (id=%s)", self.name, self.id)
        return self._fetch_event_pages(
            lambda p: self._provider.get_team_fixtures(cid, page=p),
            max_events=max_events,
            before=_normalize_dt(before),
            after=_normalize_dt(after),
            ascending=True,
        )

    def results(
        self,
        *,
        max_events: int | None = None,
        before: date | datetime | None = None,
        after: date | datetime | None = None,
    ) -> list[Event]:
        """Fetch results for this competitor.

        Defaults to events starting before *now*.

        Args:
            max_events: Stop after collecting this many events.
            before: Only events starting strictly before this date/datetime.
                    Defaults to now.
            after:  Only events starting strictly after this date/datetime.
        """
        if before is None:
            before = datetime.now()

        cid = str(self.id)

        if self._source == "raw_player":
            logger.debug("Fetching results for player '%s' (id=%s)", self.name, self.id)
            return self._fetch_event_pages(
                lambda p: self._provider.get_player_results(cid, page=p),
                max_events=max_events,
                before=_normalize_dt(before),
                after=_normalize_dt(after),
                ascending=False,
            )

        logger.debug("Fetching results for team '%s' (id=%s)", self.name, self.id)
        return self._fetch_event_pages(
            lambda p: self._provider.get_team_results(cid, page=p),
            max_events=max_events,
            before=_normalize_dt(before),
            after=_normalize_dt(after),
            ascending=False,
        )

    # -- Internal ------------------------------------------------------ #

    def _load_full(self) -> None:
        if self._full_loaded:
            return
        if self._source == "raw_player":
            logger.debug("Loading full data for player '%s' (id=%s)", self.name, self.id)
            self._raw.update(self._provider.get_player(str(self.id)))
        else:
            logger.debug("Loading full data for team '%s' (id=%s)", self.name, self.id)
            self._raw.update(self._provider.get_team(str(self.id)))
        self._full_loaded = True


# =====================================================================
# Detail dataclasses
# =====================================================================

@dataclass(frozen=True)
class TeamDetails:
    disabled: Optional[bool]
    founded: Optional[date]
    primary_competition: Optional[Competition]


@dataclass(frozen=True)
class PlayerDetails:
    number: Optional[int]
    position: Optional[str]
    weight: Optional[float]
    height: Optional[float]
    birth_place: Optional[str]
    birth_date: Optional[date]
    retired: Optional[bool]
    deceased: Optional[bool]
    market_value: Optional[Amount]
    salary: Optional[Amount]
    handedness: Optional[str]
    preferred_foot: Optional[str]
    current_earnings: Optional[Amount]
    career_earnings: Optional[Amount]
    ranking: Optional[int]


# =====================================================================
# Manager
# =====================================================================

class Manager(BaseEntity):
    """A team manager / head coach."""

    def __init__(
        self,
        *,
        id: int,
        slug: str,
        name: str,
        short_name: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.id = id
        self.slug = slug
        self.name = name
        self.short_name = short_name

        self._sport: Optional[Sport] = None
        self._country: Optional[Country] = None
        self._team: Optional[Competitor] = None
        self._performance: Optional[Performance] = None
        self._preferred_formation: Optional[str] = None

    @classmethod
    def _from_raw(cls, raw: dict | None) -> Optional[Manager]:
        """Build from a RawManager dict."""
        if not raw or "id" not in raw:
            return None

        mgr = cls(
            id=raw["id"],
            slug=raw.get("slug", ""),
            name=raw.get("name", ""),
            short_name=raw.get("shortName"),
        )
        mgr._raw = raw

        from .core import Sport, Country
        if "sport" in raw and raw["sport"]:
            mgr._sport = Sport._from_raw(raw["sport"])
        if "country" in raw and raw["country"]:
            mgr._country = Country._from_raw(raw["country"])

        return mgr

    @property
    def sport(self) -> Optional[Sport]:
        if self._sport is None:
            from .core import Sport
            raw_sport = self._raw.get("sport")
            if not raw_sport:
                self._load_full()
                raw_sport = self._raw.get("sport")
            if raw_sport:
                self._sport = Sport._from_raw(raw_sport)
        return self._sport

    @property
    def country(self) -> Optional[Country]:
        if self._country is None:
            from .core import Country
            raw_country = self._raw.get("country")
            if not raw_country:
                self._load_full()
                raw_country = self._raw.get("country")
            if raw_country:
                self._country = Country._from_raw(raw_country)
        return self._country

    @property
    def team(self) -> Optional[Competitor]:
        """The team this manager currently manages."""
        if self._team is not None:
            return self._team
        self._load_full()
        if "team" in self._raw and self._raw["team"]:
            self._team = Competitor._from_raw_team(self._raw["team"])
        return self._team

    @property
    def performance(self) -> Optional[Performance]:
        """Career performance stats."""
        if self._performance is not None:
            return self._performance
        self._load_full()
        self._performance = _performance_from_raw(self._raw.get("performance"))
        return self._performance

    @property
    def preferred_formation(self) -> Optional[str]:
        if self._preferred_formation is not None:
            return self._preferred_formation
        self._load_full()
        self._preferred_formation = self._raw.get("preferredFormation")
        return self._preferred_formation

    def _load_full(self) -> None:
        if self._full_loaded:
            return
        logger.debug("Loading full data for manager '%s' (id=%s)", self.name, self.id)
        self._raw.update(self._provider.get_manager(str(self.id)))
        self._full_loaded = True

    # -- Event fetching ------------------------------------------------ #

    def events(
        self,
        *,
        max_events: int | None = None,
        before: date | datetime | None = None,
        after: date | datetime | None = None,
    ) -> list[Event]:
        """Fetch all events managed by this manager.

        Only a results endpoint is available — returns past events only.

        Args:
            max_events: Stop after collecting this many events.
            before: Only events starting strictly before this date/datetime.
            after:  Only events starting strictly after this date/datetime.
        """
        mid = str(self.id)
        logger.debug("Fetching events for manager '%s' (id=%s)", self.name, self.id)
        return self._fetch_event_pages(
            lambda p: self._provider.get_manager_results(mid, page=p),
            max_events=max_events,
            before=_normalize_dt(before),
            after=_normalize_dt(after),
            ascending=False,
        )

    def results(
        self,
        *,
        max_events: int | None = None,
        before: date | datetime | None = None,
        after: date | datetime | None = None,
    ) -> list[Event]:
        """Fetch results for this manager.

        Defaults to events starting before *now*.

        Args:
            max_events: Stop after collecting this many events.
            before: Only events starting strictly before this date/datetime.
                    Defaults to now.
            after:  Only events starting strictly after this date/datetime.
        """
        if before is None:
            before = datetime.now()
        mid = str(self.id)
        logger.debug("Fetching results for manager '%s' (id=%s)", self.name, self.id)
        return self._fetch_event_pages(
            lambda p: self._provider.get_manager_results(mid, page=p),
            max_events=max_events,
            before=_normalize_dt(before),
            after=_normalize_dt(after),
            ascending=False,
        )


# =====================================================================
# Referee
# =====================================================================

class Referee(BaseEntity):
    """A match referee / umpire."""

    def __init__(
        self,
        *,
        id: int,
        slug: str,
        name: str,
    ) -> None:
        super().__init__()
        self.id = id
        self.slug = slug
        self.name = name

        self._sport: Optional[Sport] = None
        self._country: Optional[Country] = None
        self._games: Optional[int] = None
        self._cards: Optional[Cards] = None

    @classmethod
    def _from_raw(cls, raw: dict | None) -> Optional[Referee]:
        """Build from a RawReferee dict."""
        if not raw or "id" not in raw:
            return None

        ref = cls(
            id=raw["id"],
            slug=raw.get("slug", ""),
            name=raw.get("name", ""),
        )
        ref._raw = raw

        from .core import Sport, Country
        if "sport" in raw and raw["sport"]:
            ref._sport = Sport._from_raw(raw["sport"])
        if "country" in raw and raw["country"]:
            ref._country = Country._from_raw(raw["country"])

        # Games and cards may already be present in the raw dict
        if "games" in raw:
            ref._games = raw["games"]
        ref._cards = _cards_from_raw(raw)

        return ref

    @property
    def sport(self) -> Optional[Sport]:
        if self._sport is None:
            from .core import Sport
            raw_sport = self._raw.get("sport")
            if not raw_sport:
                self._load_full()
                raw_sport = self._raw.get("sport")
            if raw_sport:
                self._sport = Sport._from_raw(raw_sport)
        return self._sport

    @property
    def country(self) -> Optional[Country]:
        if self._country is None:
            from .core import Country
            raw_country = self._raw.get("country")
            if not raw_country:
                self._load_full()
                raw_country = self._raw.get("country")
            if raw_country:
                self._country = Country._from_raw(raw_country)
        return self._country

    @property
    def games(self) -> Optional[int]:
        if self._games is None:
            self._load_full()
            self._games = self._raw.get("games")
        return self._games

    @property
    def cards(self) -> Optional[Cards]:
        if self._cards is None:
            self._load_full()
            self._cards = _cards_from_raw(self._raw)
        return self._cards

    def _load_full(self) -> None:
        if self._full_loaded:
            return
        logger.debug("Loading full data for referee '%s' (id=%s)", self.name, self.id)
        self._raw.update(self._provider.get_referee(str(self.id)))
        self._full_loaded = True

    # -- Event fetching ------------------------------------------------ #

    def events(
        self,
        *,
        max_events: int | None = None,
        before: date | datetime | None = None,
        after: date | datetime | None = None,
    ) -> list[Event]:
        """Fetch all events officiated by this referee.

        Only a results endpoint is available — returns past events only.

        Args:
            max_events: Stop after collecting this many events.
            before: Only events starting strictly before this date/datetime.
            after:  Only events starting strictly after this date/datetime.
        """
        rid = str(self.id)
        logger.debug("Fetching events for referee '%s' (id=%s)", self.name, self.id)
        return self._fetch_event_pages(
            lambda p: self._provider.get_referee_results(rid, page=p),
            max_events=max_events,
            before=_normalize_dt(before),
            after=_normalize_dt(after),
            ascending=False,
        )

    def results(
        self,
        *,
        max_events: int | None = None,
        before: date | datetime | None = None,
        after: date | datetime | None = None,
    ) -> list[Event]:
        """Fetch results for this referee.

        Defaults to events starting before *now*.

        Args:
            max_events: Stop after collecting this many events.
            before: Only events starting strictly before this date/datetime.
                    Defaults to now.
            after:  Only events starting strictly after this date/datetime.
        """
        if before is None:
            before = datetime.now()
        rid = str(self.id)
        logger.debug("Fetching results for referee '%s' (id=%s)", self.name, self.id)
        return self._fetch_event_pages(
            lambda p: self._provider.get_referee_results(rid, page=p),
            max_events=max_events,
            before=_normalize_dt(before),
            after=_normalize_dt(after),
            ascending=False,
        )


# Needed at module level for type annotations
from .core import Sport, Country, Category  # noqa: E402
