# Welcome to sport-index

**A unified Python SDK for exploring sports data through a single object-oriented API.**

!!! warning "Disclaimer"
    This package relies on unofficial provider endpoints. Availability and payloads may change at any time. Use responsibly and comply with each provider's Terms of Service.

`sport-index` provides a coherent Python API across multiple sports domains. Instead of manually traversing provider-specific endpoints and parsing raw JSON, you work with **Python entities and relations**. 

Data is strictly lazy-loaded: network calls are only made exactly when you request the data.

---

## Installation

You can install the package directly from GitHub:

```bash
pip install "git+https://github.com/JolanDUBOIS/sport-index.git"
```

---

## The Core Concept: Graph Navigation

The true power of `sport-index` is how you navigate between entities. You don't need to memorize a dozen different client methods; you just follow the logical relationships of the sport.

Here is what a typical flow looks like:

```python
from sportindex import Sport, SportClient

client = SportClient()

# 1. Pick a sport
sport = client.list(Sport).get(name="Football")

# 2. Navigate the domain relationships naturally
category = sport.categories.get(name="England")
competition = category.competitions.get(name="Premier League")
season = competition.seasons[0]

# 3. Access the data you actually care about
standings = season.standings
fixtures = season.get_fixtures()
results = season.get_results()

# 4. Inspect specific events
event = (results or fixtures)[0]
print(event.name)
print(event.lineups)   # MatchEvent only
```

!!! note "`seasons[0]` is the newest season, not necessarily the live one"
    The provider often creates a season months before it starts, so the newest entry may have
    no standings or events yet. Select deliberately — for example
    `competition.seasons.get(year="24/25")` — when you need a season with data.

## Finding Specific Entities

If you don't want to drill down from the top-level sport, `SportClient.search` works across
every searchable entity type:

```python
from sportindex import Competitor, Manager, Referee, StageEvent, Venue

# Find a team directly
competitors = client.search(Competitor, "Paris Saint-Germain")
team = competitors[0].resolve()          # Competitor -> Team
print(team.name, len(team.get_results()), team.manager)

# Find a race: each edition of the Tour de France is a StageEvent
races = client.search(StageEvent, "Tour de France")

# Search for staff or venues
managers = client.search(Manager, "Luis Enrique")
referees = client.search(Referee, "Turpin")
venues = client.search(Venue, "Parc des Princes")
```

## Looking Entities Up by ID

Every entity has a string **SDK ID** — a type prefix plus the provider's numeric ID:

```python
competition = client.get("trnc:7")           # class inferred from the prefix
competition = client.get("trnc:7", Competition)   # or state it explicitly
```

---

## Next Steps

Ready to see every tool at your disposal?

👉 **[Dive into the API Reference](api.md)** to see the complete list of available models, properties, and methods.
