# sport-index

Unified Python SDK for exploring sports data through a single object-oriented API.

> **Disclaimer**
> This package relies on unofficial provider endpoints. Availability and payload shape may change at any time.
> Use responsibly and ensure your usage complies with each provider's Terms of Service.

## Why sport-index?

`sport-index` gives you one coherent API over multiple sports domains:

- sports, categories, competitions, seasons
- events (matches and races)
- competitors (teams and players)
- managers, referees, venues
- standings and rankings

Instead of manually traversing provider-specific routes, you work with Python entities and relations (`competition -> seasons -> events`, etc.).

## Current status

- **Stage:** early public version (`0.1.x`)
- **Main UX:** domain entities and relationships
- **Provider:** Sofascore (parsed + normalized)
- **Focus:** practical data exploration and scripting

## Installation

### From GitHub (pip)

```bash
pip install "git+https://github.com/JolanDUBOIS/sport-index.git"
```

### For local development (Poetry)

```bash
poetry install
poetry shell
```

## Quick start

```python
from sportindex import SportClient

client = SportClient()

# Discover available sports
sports = client.list_sports()
football = sports.search("football").get(name="Football")

print(football)
print(f"Total sports available: {len(sports)}")
```

`SportClient` is the bootstrap layer. The core experience starts once you navigate entity relationships.

## Typical navigation flow

```python
from sportindex import SportClient

client = SportClient()

# 1) pick a sport
sport = client.list_sports().search("football")[0]

# 2) navigate through domain relationships
category = sport.categories[0]
competition = category.competitions[0]
season = competition.seasons[0]

# 3) pull dynamic season data
standings = season.standings
fixtures = season.get_fixtures()
results = season.get_results()

# 4) inspect events and enriched event details
event = (results or fixtures)[0]
lineups = event.lineups
h2h = event.h2h

print(f"{competition.name} / {season.name}")
print(f"standings={len(standings)} fixtures={len(fixtures)} results={len(results)}")
print(f"event={event.name} lineups={'yes' if lineups else 'no'} h2h={'yes' if h2h else 'no'}")
```

## Search examples

```python
from sportindex import SportClient

client = SportClient()

# Competitors
teams_or_players = client.search_competitors("Paris Saint-Germain")
if teams_or_players:
    competitor = teams_or_players[0]

    # direct domain methods
    recent_results = competitor.get_results()
    upcoming_fixtures = competitor.get_fixtures()
    print(competitor.name, len(recent_results), len(upcoming_fixtures))

# Managers / referees / venues
print(client.search_managers("Luis Enrique")[:3])
print(client.search_referees("Turpin")[:3])
print(client.search_venues("Parc des Princes")[:3])
```

## Domain model overview

The package is designed around graph-like navigation:

- `sport.categories`
- `category.competitions`
- `competition.seasons`
- `season.standings`, `season.get_fixtures()`, `season.get_results()`, `season.get_events()`
- `event.competition`, `event.season`, `event.competitors`, `event.lineups`, `event.statistics`, `event.h2h`
- `competitor.get_results()`, `competitor.get_fixtures()`, `competitor.players`, `competitor.manager`, `competitor.venue`

Most network-backed fields are lazy: data is fetched when you access the property/method.

## API bootstrap overview

`SportClient` currently exposes:

- `list_sports()`, `get_sport()`, `search_sports()`
- `list_categories(sport_id)`
- `list_competitions(sport_id, category_id)`, `get_competition()`
- `list_seasons(competition_id)`
- `get_event()`
- `get_competitor()`, `search_competitors()`
- `get_manager()`, `search_managers()`
- `get_referee()`, `search_referees()`
- `get_venue()`, `search_venues()`
- `clear_cache(namespace=None)`

Think of `SportClient` as a finder/bootstrap utility; most day-to-day usage happens on domain entities.

## Caching

`SportClient` maintains an in-memory entity cache by namespace (`events`, `competitions`, `competitors`, ...).

```python
client.clear_cache()              # clear everything
client.clear_cache("events")     # clear only one namespace
```

## Errors and resilience

Provider-level exceptions are exposed at package root:

```python
from sportindex import NotFoundError, RateLimitError, FetchError
```

Many endpoints are best-effort: some fields may be absent depending on sport, competition, or provider payload.

## Version

```python
import sportindex
print(sportindex.__version__)
```

## Contributing

Issues and PRs are welcome.

If you report a bug, please include:

- the code snippet you ran
- the entity IDs or query used
- traceback/error message
- (ideally) a minimal reproducible example