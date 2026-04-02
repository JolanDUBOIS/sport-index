![Docs](https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat-square)

# sport-index

Unified Python SDK for exploring sports data through a single object-oriented API.

> **Disclaimer**  
> This package relies on unofficial provider endpoints. Availability and payloads may change at any time. Use responsibly and comply with each provider's Terms of Service.

The full API Reference, domain model overview, and user guide can be found here: [sport-index Documentation](https://JolanDUBOIS.github.io/sport-index/)

## Overview

`sport-index` provides a coherent Python API across multiple sports domains:

- Sports, categories, competitions, seasons
- Events (matches and races)
- Competitors (teams, players)
- Managers, referees, venues
- Standings and rankings

Instead of manually traversing provider-specific endpoints, you work with **Python entities and relations**, e.g., `competition -> seasons -> events`.

## Installation

### From GitHub

```bash
pip install "git+https://github.com/JolanDUBOIS/sport-index.git"
```

### Local development (Poetry)

```bash
poetry install
poetry shell
```

## Quick Start

```python
from sportindex import SportClient

client = SportClient()

# List available sports
sports = client.list_sports()
football = sports.search("football").get(name="Football")

print(football)
print(f"Total sports available: {len(sports)}")
```

The **core experience starts once you navigate entity relationships**.

## Typical Navigation Flow

```python
client = SportClient()

# Pick a sport
sport = client.list_sports().search("football")[0]

# Navigate domain relationships
category = sport.categories[0]
competition = category.competitions[0]
season = competition.seasons[0]

# Access season data
standings = season.standings
fixtures = season.get_fixtures()
results = season.get_results()

# Inspect events
event = (results or fixtures)[0]
print(event.name, event.lineups, event.h2h)
```

All network-backed fields are **lazy-loaded**: data is fetched when accessed.

## Search Examples

```python
# Search competitors
competitors = client.search_competitors("Paris Saint-Germain")
if competitors:
    team = competitors[0]
    print(team.name, len(team.get_results()), len(team.get_fixtures()))

# Search managers, referees, venues
print(client.search_managers("Luis Enrique")[:3])
print(client.search_referees("Turpin")[:3])
print(client.search_venues("Parc des Princes")[:3])
```

## Domain Model Overview

* `sport.categories` → `category.competitions` → `competition.seasons`
* `season.standings`, `season.get_fixtures()`, `season.get_results()`
* `event.competition`, `event.season`, `event.competitors`, `event.lineups`, `event.statistics`, `event.h2h`
* `competitor.get_results()`, `competitor.get_fixtures()`, `competitor.players`, `competitor.manager`, `competitor.venue`

This **graph-like navigation** is the core of `sport-index`.

## API Bootstrap: SportClient

`SportClient` provides finder and bootstrap utilities:

* `list_sports()`, `get_sport()`, `search_sports()`
* `list_categories(sport_id)`
* `list_competitions(sport_id, category_id)`, `get_competition()`
* `list_seasons(competition_id)`
* `get_event()`
* `get_competitor()`, `search_competitors()`
* `get_manager()`, `search_managers()`
* `get_referee()`, `search_referees()`
* `get_venue()`, `search_venues()`
* `clear_cache(namespace=None)`

Most usage happens **via domain entities**, not direct client calls.

## Caching

In-memory entity cache by namespace:

```python
client.clear_cache()            # clear everything
client.clear_cache("events")    # clear a single namespace
```

## Offline Testing & Mocking

`sport-index` ships with a built-in "Record and Replay" (VCR) fetcher. This allows you to write tests for your own applications using deterministic, local data without hitting the real API or dealing with rate limits during CI/CD.

This is controlled entirely via environment variables:

  * `SPORTINDEX_RECORD_MODE`: Set to `record` (fetches from API and saves to disk) or `replay` (loads from disk).
  * `SPORTINDEX_FIXTURES_DIR`: The path where JSON mock files should be saved/loaded (defaults to `tests/fixtures`).

**Recommended Pytest Setup (`conftest.py`):**
To ensure your test suite automatically uses offline fixtures, add this to your `conftest.py`:

```python
import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def setup_sportindex_offline():
    os.environ["SPORTINDEX_RECORD_MODE"] = os.environ.get("SPORTINDEX_RECORD_MODE") or "replay"
    os.environ["SPORTINDEX_FIXTURES_DIR"] = "tests/fixtures"
    yield
    os.environ.pop("SPORTINDEX_RECORD_MODE", None)
```

**Recording New Data:**
When writing a new test that calls an unrecorded endpoint, simply run Pytest with the record mode active via the CLI:

```bash
SPORTINDEX_RECORD_MODE=record pytest
```

The SDK will intercept the HTTP requests, generate safe filenames based on the API paths, and save the exact responses to your fixtures directory. By committing these JSON files to your repository, subsequent test executions become fully deterministic, execute without network latency, and remain completely isolated from upstream rate limits or outages.

## Exceptions & Error Handling

All exceptions are in `sportindex.exceptions`:

```python
from sportindex.exceptions import (
    ProviderNotFoundError, RateLimitError, FetchError,
    NetworkError, ParseError, EntityNotFoundError,
    InsufficientDataError, DomainError,
)
```

### Semantics

* **Provider-level errors**: `ProviderNotFoundError` (404), `RateLimitError` (429), `FetchError` (network), `NetworkError` (timeouts), `ParseError` (parsing).
* **Domain-level errors**: `EntityNotFoundError`, `InsufficientDataError`, `DomainError`.

**Best practices:**

```python
# Tolerant lookup
event = client.get_event(12345)
if event is None:
    print("Event not found")

# Strict listing (raises on missing)
try:
    competitions = client.list_competitions(sport_id=1, category_id=2)
except EntityNotFoundError:
    print("Invalid sport or category")

# Handle provider/network issues
try:
    ev = client.get_event(12345)
except (ProviderNotFoundError, FetchError, RateLimitError) as exc:
    # retry or propagate
    raise
```

## Version

```python
import sportindex
print(sportindex.__version__)
```

## Contributing

Issues and PRs welcome. Include:

* Code snippet
* Entity IDs or query used
* Traceback/error message
* Minimal reproducible example (if possible)
