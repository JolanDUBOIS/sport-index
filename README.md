![Docs](https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat-square)
![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square)
![License](https://img.shields.io/github/license/JolanDUBOIS/sport-index?style=flat-square)

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

**Key Features:**
- **Zero Configuration:** No API keys, accounts, or `.env` files required to start fetching data.
- **Object-Oriented:** Instead of manually traversing provider-specific endpoints, you work with Python entities and relations (e.g., `competition -> seasons -> events`).

## Installation

### From GitHub

```bash
pip install "git+https://github.com/JolanDUBOIS/sport-index.git"
```

### Local development

```bash
uv sync            # installs the project and its dev dependencies
uv run pytest      # offline unit tests
```

## Entity IDs

Every entity is addressed by a string **SDK ID**: a short type prefix, then the provider's numeric ID — `"spt:1"` (Football), `"trnc:7"` (UEFA Champions League), `"vnu:843"` (Parc des Princes). Entities that only exist inside a parent nest their parent's ID, so a season reads `"trnc:7:trns:61644"`.

You rarely write these by hand: you get them from `search()`, `list()`, or by navigating from another entity.

## Quick Start

```python
from sportindex import SportClient, Competition, Sport

client = SportClient()

# Look an entity up by its SDK ID. The class is optional — it is inferred from the prefix.
ucl = client.get("trnc:7")
print(ucl)

# Or find it by name
ucl = client.search(Competition, "UEFA Champions League")[0]
print(ucl)

sports = client.list(Sport)
football = sports.get(name="Football")
print(football)
print(f"Total sports available: {len(sports)}")
```

The **core experience starts once you navigate entity relationships**.

## Typical Navigation Flow

```python
client = SportClient()

# Pick a sport
sport = client.list(Sport).get(name="Football")

# Navigate domain relationships
category = sport.categories.get(name="England")
competition = category.competitions.get(name="Premier League")

# seasons[0] is the *newest* season, which the provider often creates months before it
# starts — so it may have no standings or events yet. Pick deliberately.
season = competition.seasons[0]

# Access season data
standings = season.standings
fixtures = season.get_fixtures()
results = season.get_results()

# Inspect events
event = (results or fixtures)[0]
print(event.name, event.lineups, event.h2h) # if MatchEvent
```

All network-backed fields are **lazy-loaded**: data is fetched when accessed.

## Search Examples

```python
from sportindex import Competitor, Event, Manager, Referee, Venue

# Search competitors
competitors = client.search(Competitor, "Paris Saint-Germain")
if competitors:
    team = competitors[0]
    print(team.name, len(team.get_results()), len(team.get_fixtures()))

# Search managers, referees, venues, events
print(client.search(Manager, "Luis Enrique")[:3])
print(client.search(Referee, "Turpin")[:3])
print(client.search(Venue, "Parc des Princes")[:3])
print(client.search(Event, "Monaco Grand Prix")[:3])
```

Searching `Event` returns matches and stages together; `MatchEvent` and `StageEvent` narrow it to one kind.

## Domain Model Overview

* `sport.categories` → `category.competitions` → `competition.seasons`
* `season.standings`, `season.get_fixtures()`, `season.get_results()`
* `event.competition`, `event.season`, `event.competitors`, `event.lineups`, `event.statistics`, `event.h2h`
* `competitor.get_results()`, `competitor.get_fixtures()`, `competitor.country`, `competitor.sport`

A `Competitor` is always a `Team` or an `Athlete`, decided from the provider's own data the moment it is built, so a side of a match, a standings row and a search result are all the same entity with the same ID:

```python
team = client.search(Competitor, "Paris Saint-Germain")[0]          # -> Team
print(team.players, team.manager, team.venue)

athlete = client.search(Competitor, "Ousmane Dembélé")[0]           # -> Athlete
print(athlete.first_name, athlete.last_name, athlete.info)
```

The classification reads the `type` field the provider sets on each team-shaped record: 0 for a club or national team, 1 for an individual (a tennis player, a driver, a rider, a fighter), 2 for a doubles pair, which is treated as a team. The provider does not document these values; they are inferred from its payloads.

This **graph-like navigation** is the core of `sport-index`.

## API Bootstrap: SportClient

`SportClient` provides finder and bootstrap utilities:

* `get(entity_id, entity_cls=None, strict=False)` — `entity_cls` is optional; when omitted the class is resolved from the ID's prefix
* `list(entity_cls, **kwargs)` — filters depend on the class: `Category` takes `sport_id`, `Competition` takes `category_id`, `Season` takes `competition_id`, `Event` takes `season_id`; `Sport` and `Country` take none
* `search(entity_cls, query, max_results=20)`
* `clear_cache(namespace=None)`

Most usage happens **via domain entities**, not direct client calls.

## Caching

In-memory entity cache by namespace:

```python
client.clear_cache()           # clear everything
client.clear_cache("event")    # clear a single namespace
```

Valid namespaces are singular: `sport`, `country`, `category`, `competition`, `season`,
`event`, `competitor`, `manager`, `referee`, `venue`. An unknown namespace raises `KeyError`.

## Offline Testing & Mocking

`sport-index` ships with a built-in "Record and Replay" (VCR) fetcher. This is strictly a **testing utility** that allows you to write tests for your own applications using deterministic local data, avoiding rate limits and network latency during test execution.

**⚠️ WARNING: This is for testing purposes only. Do not enable SPORTINDEX_RECORD_MODE in a production environment. Because sports data (like daily fixtures) constantly changes, this is strictly a mocking tool, not a caching layer, and will serve hardcoded, stale data if left active.**

### Configuration
This is controlled entirely via environment variables during your test runs:

* **`SPORTINDEX_RECORD_MODE`**: unset by default, in which case the client runs **live** and
  no fixtures are used. Set it to one of:
    * `replay`: Loads from disk; raises if a fixture is missing. **Use this in CI/CD** — it is
      the only mode that guarantees no network access.
    * `auto`: Loads from disk if available; otherwise fetches from the API and records the
      result. **Recommended for local test development.** Note that a missing fixture silently
      becomes a live request.
    * `record`: Always fetches from the API and overwrites existing fixtures. Use this to
      update your mocks.
* **`SPORTINDEX_FIXTURES_DIR`**: The path where JSON mock files are stored (defaults to `tests/fixtures`).

### Failures Are Recorded Too

A fixture stores the response **status** alongside the body, so a call that legitimately fails is a recordable outcome like any other. A 404 recorded from the provider replays as `ProviderNotFoundError`, a 429 as `RateLimitError` — without touching the network. This means a code path that is *supposed* to 404 can be covered by an offline test, and that `auto` mode stops re-fetching such a call on every run.

Fixtures recorded before statuses were stored hold a bare response body. They still replay, as a 200; re-record them if you want the status captured.

### Recommended Testing Workflow

| Environment | Mode | Benefit |
| :--- | :--- | :--- |
| **Local Test Dev** | `auto` | Fast execution for existing tests; automatically records new tests without manual intervention. |
| **CI / Automated Tests** | `replay` | Ensures builds are deterministic and don't fail due to external API outages or rate limits. |
| **Test Refactoring** | `record` | Refreshes all local data to ensure your mocks match the latest upstream API schema. |

**Setup for Pytest (`conftest.py`):**

To ensure your test suite automatically uses offline fixtures, add this to your `conftest.py`:

```python
import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def setup_sportindex_offline():
    os.environ["SPORTINDEX_RECORD_MODE"] = os.environ.get("SPORTINDEX_RECORD_MODE") or "auto"
    os.environ["SPORTINDEX_FIXTURES_DIR"] = "tests/fixtures"
    yield
```

**Workflow Example:**
When writing a new test, you don't need to do anything special. Because the mode is `auto`, the first time you run the test, the SDK will hit the API and save the response. Every subsequent run of that test will be instant and offline.

To force-refresh your test data:
```bash
SPORTINDEX_RECORD_MODE=record pytest
```

The SDK will intercept the HTTP requests, generate safe filenames based on the API paths, and save the exact responses — status included — to your fixtures directory. By committing these JSON files to your repository, subsequent test executions become fully deterministic, execute without network latency, and remain completely isolated from upstream rate limits or outages.

## Exceptions & Error Handling

All exceptions are in `sportindex.exceptions`:

```python
from sportindex.exceptions import (
    ProviderNotFoundError, RateLimitError, FetchError, ChallengeError,
    NetworkError, ParseError, EntityNotFoundError,
    InsufficientDataError, DomainError,
)
```

### Semantics

* **Provider-level errors**: `ProviderNotFoundError` (404), `RateLimitError` (429), `FetchError` (any other failed fetch), `NetworkError` (provider unreachable on every attempt: connection, DNS, timeouts; a subclass of `FetchError`), `ChallengeError` (403 bot challenge), `ParseError` (parsing).
* **Domain-level errors**: `EntityNotFoundError`, `InsufficientDataError`, `DomainError`.

`ChallengeError` is worth catching separately: it means the provider challenged the request rather than refusing it, which in practice means the traffic left from a VPN or datacenter IP range. Retrying will not clear it — the fix is to run from an ordinary connection.

**Best practices:**

```python
# Tolerant or strict lookup
event = client.get("mch:12345")
if event is None:
    print("Event not found")

try:
    event = client.get("mch:12345", strict=True)
except EntityNotFoundError:
    print("Event not found")

# Strict listing (raises when the required filter is missing or matches nothing)
try:
    competitions = client.list(Competition, category_id="cat:1", sport_id="spt:1")
except EntityNotFoundError:
    print("Invalid sport or category")

# Handle provider/network issues
try:
    ev = client.get("mch:12345")
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

## License

MIT — see [LICENSE](LICENSE).

This covers the `sport-index` source code only. It grants no rights over the data returned by the providers it queries — see the disclaimer at the top.