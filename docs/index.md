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
from sportindex import SportClient

client = SportClient()

# 1. Pick a sport
sport = client.list_sports().search("football")

# 2. Navigate the domain relationships naturally
category = sport.categories
competition = category.competitions
season = competition.seasons

# 3. Access the data you actually care about
standings = season.standings
fixtures = season.get_fixtures()
results = season.get_results()

# 4. Inspect specific events
event = results
print(event.name)
print(event.lineups)
```

## Finding Specific Entities

If you don't want to drill down from the top-level sport, the `SportClient` acts as a powerful search engine for specific domains:

```python
# Find a team directly
competitors = client.search_competitors("Paris Saint-Germain")
team = competitors
print(team.name, len(team.get_results()))

# Search for staff or venues
managers = client.search_managers("Luis Enrique")
referees = client.search_referees("Turpin")
venues = client.search_venues("Parc des Princes")
```

---

## Next Steps

Ready to see every tool at your disposal?

👉 **[Dive into the API Reference](api.md)** to see the complete list of available models, properties, and methods.
