# sport-index

Unified Python clients for sports data from unofficial sources.

> **DISCLAIMER:** This library accesses unofficial APIs and may rely on scraping in the future. Use responsibly and comply with the terms of service of the data providers. The library is intended for personal or research use only.

## Overview

`sport-index` provides Python clients for multiple sports, giving you easy access to curated, simplified JSON data. Each client abstracts a provider, returning data in a consistent format that resembles a clean API.

- **Simplified JSON:** Only relevant fields are returned; raw provider data is lightly transformed for clarity.
- **Client abstraction:** Users interact with high-level sport clients (e.g., FootballClient) rather than the underlying provider.
- **Stable within 0.x:** Outputs are usable and complete, as long as the underlying provider is available.

Current focus: football ([OneFootball](https://onefootball.com)) and f1 ([ESPN](https://www.espn.com)), with other sports in progress.

## Installation

The repository is not on PyPI at the moment, to install it via pip, you must run:

```bash
pip install https://github.com/JolanDUBOIS/sport-index.git#egg=sport-index
```

## Quick Example

```python
from sportindex.football import FootballClient

# Initialize client
client = FootballClient()

# Get all matches for a specific team
matches = client.get_team_fixtures(team_id="psg-263")
for match in matches["matches"]:
    print(f'{match["datetime"]}: {match["home_team"]["name"]} vs {match["away_team"]["name"]}')
```

## Version

```python
import sportindex
print(sportindex.__version__)
```