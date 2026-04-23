# game_data

An NBA data pipeline that pulls stats from the [balldontlie API](https://www.balldontlie.io/) and saves them locally as CSVs.

## Stack

- Python, `balldontlie` SDK, `pandas`, `python-dotenv` for API key management
- `psycopg2-binary` included for a planned Postgres integration

## How it works

`extract.py` contains 4 functions that each fetch a dataset and write it to a CSV:

| Function | Output | Description |
|---|---|---|
| `getTeamNames()` | `teams.csv` | All 30 NBA teams with IDs, city, conference, division |
| `getPlayers()` | `players.csv` | All active players with team IDs (paginated) |
| `getGamesForCurrentSeason()` | `games.csv` | All 2025 season games with scores and team info |
| `getGameStats()` | `game_stats.csv` | Per-player box scores for every game (pts, reb, ast, shooting splits, etc.) |

`getGameStats()` iterates over every game ID, handles rate limiting with exponential backoff retries, and appends results to `game_stats.csv`.

## Data

- `games.csv` — ~40 games
- `players.csv` — ~530 active players
- `game_stats.csv` — ~7,700 rows of player box score stats

## Setup

1. Create a `.env` file with your balldontlie API key:
   ```
   AUTH_KEY=your_api_key_here
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run `extract.py` directly to fetch game stats, or uncomment the other function calls in `__main__` as needed.

## Status

Early stage. Data extraction is working and CSVs are populated. A database layer (`models.py`) and analysis code are planned but not yet implemented.
