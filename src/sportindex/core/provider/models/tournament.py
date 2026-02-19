from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .core import BaseModel, Country, Category
from .team import Team
from .utils import timestamp_to_iso


@dataclass(frozen=True, kw_only=True)
class Season(BaseModel):
    id: str
    name: str
    year: str

    # Extras
    start: Optional[str]
    description: Optional[str]

    @classmethod
    def _from_api(cls, raw: dict) -> Season:
        return Season(
            id=raw.get("id"),
            name=raw.get("name"),
            year=raw.get("year"),
            start=timestamp_to_iso(raw.get("startDateTimestamp"), kind="date"),
            description=raw.get("description"),
        )

@dataclass(frozen=True, kw_only=True)
class UniqueTournament(BaseModel):
    id: str
    slug: str
    name: str
    category: Category

    # Extras
    gender: Optional[str] = None
    tier: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    founded: Optional[int] = None
    country: Optional[Country] = None
    upper_divisions: Optional[list[UniqueTournament]] = None
    lower_divisions: Optional[list[UniqueTournament]] = None
    title_holder: Optional[Team] = None
    most_titles_teams: Optional[list[Team]] = None
    linked_unique_tournaments: Optional[list[UniqueTournament]] = None
    # numberOfCompetitors, numberOfDivisions, owner...

    @classmethod
    def _from_api(cls, raw: dict) -> UniqueTournament:
        return UniqueTournament(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            gender=raw.get("gender"),
            category=Category.from_api(raw.get("category")),
            country=Country.from_api(raw.get("country")),
            tier=raw.get("tier"),
            start=timestamp_to_iso(raw.get("startDateTimestamp"), kind="date"),
            end=timestamp_to_iso(raw.get("endDateTimestamp"), kind="date"),
            founded=raw.get("yearOfFoundation"),
            upper_divisions=[UniqueTournament.from_api(comp) for comp in raw.get("upperDivisions", [])],
            lower_divisions=[UniqueTournament.from_api(comp) for comp in raw.get("lowerDivisions", [])],
            title_holder=Team.from_api(raw.get("titleHolder")),
            most_titles_teams=[Team.from_api(team) for team in raw.get("mostTitlesTeams", [])],
            linked_unique_tournaments=[UniqueTournament.from_api(comp) for comp in raw.get("linkedUniqueTournaments", [])],
        )

@dataclass(frozen=True, kw_only=True)
class Tournament(BaseModel):
    id: str
    slug: str
    name: str
    category: Category
    unique_tournament: UniqueTournament

    @classmethod
    def _from_api(cls, raw: dict) -> Tournament:
        return Tournament(
            id=raw.get("id"),
            slug=raw.get("slug"),
            name=raw.get("name"),
            category=Category.from_api(raw.get("category")),
            unique_tournament=UniqueTournament.from_api(raw.get("uniqueTournament")),
        )

@dataclass(frozen=True, kw_only=True)
class UniqueTournamentSeasons(BaseModel):
    unique_tournament: UniqueTournament
    seasons: list[Season]

    @classmethod
    def _from_api(cls, raw: dict) -> UniqueTournamentSeasons:
        return UniqueTournamentSeasons(
            unique_tournament=UniqueTournament.from_api(raw.get("uniqueTournament")),
            seasons=[Season._from_api(season) for season in raw.get("seasons", [])],
        )
