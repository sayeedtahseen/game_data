# game_data

An NBA data pipeline that pulls stats from the [balldontlie API](https://www.balldontlie.io/), saves them as CSVs, and loads them into a PostgreSQL database.

## Stack

- Python, `balldontlie` SDK, `pandas`, `python-dotenv`
- `sqlalchemy` + `psycopg2-binary` for database writes
- PostgreSQL 16 running in Docker

## How it works

`extract.py` has two layers of functions:

### API → CSV

| Function | Output | Description |
|---|---|---|
| `getTeamNames()` | `teams.csv` | All 30 NBA teams with IDs, city, conference, division |
| `getPlayers()` | `players.csv` | All active players with team IDs (paginated) |
| `getGamesForCurrentSeason()` | `games.csv` | All 2025 season games with scores and team info |
| `getAllGameStats()` | `game_stats.csv` | Per-player box scores for every game (pts, reb, ast, shooting splits, etc.) |

`getAllGameStats()` iterates over every game ID, handles rate limiting with exponential backoff retries, and appends results to `game_stats.csv`.

### CSV → Database

| Function | Table | Description |
|---|---|---|
| `readTeamListCSV()` | `teams` | Reads `teams.csv` and writes to DB |
| `readGamesListCSV()` | `games` | Reads `games.csv` and writes to DB |

## Data

- `teams.csv` — 30 NBA teams
- `games.csv` — ~40 games
- `players.csv` — ~530 active players
- `game_stats.csv` — ~7,700 rows of player box score stats

## Setup

### 1. Environment variables

Create a `.env` file in the project root:

```
AUTH_KEY=your_balldontlie_api_key
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=game_data
DB_PORT=5332
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the database

```bash
docker compose up -d
```

This starts a PostgreSQL container on port `5332` and automatically runs the schema files in `./sql/`.

### 4. Run the pipeline

Uncomment the relevant function calls in `__main__` in `extract.py` and run:

```bash
python extract.py
```

### Connecting to the database from Python

```python
from sqlalchemy import create_engine
import os

engine = create_engine(
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:{os.getenv('DB_PORT')}/{os.getenv('POSTGRES_DB')}"
)
```

### Connecting via psql

```bash
psql -h localhost -p 5332 -U postgres -d game_data
```

## Resetting the database

```bash
docker compose down -v
docker compose up -d
```

The `-v` flag removes the volume so Postgres reinitializes and re-runs the SQL schema files from scratch.

## Status

Data extraction and CSV export are working. Database schema is defined and Postgres loads automatically via Docker. CSV → DB loading is implemented for teams and games.
