# game_data

An NBA data pipeline that pulls stats from the [balldontlie API](https://www.balldontlie.io/) and loads them into a PostgreSQL database, orchestrated with Apache Airflow.

## Stack

- Python, `balldontlie` SDK, `pandas`, `python-dotenv`
- `sqlalchemy` + `psycopg2-binary` for database writes
- PostgreSQL 16 running in Docker
- Apache Airflow for orchestration

## Architecture

```
extract_layer.py  →  initial_load_dag.py  →  load_layer.py  →  PostgreSQL
```

### `extract_layer.py`

Fetches data from the balldontlie API and returns JSON strings (`orient='records'`). All functions handle rate limiting with exponential backoff (up to 3 retries).

| Function | Description |
|---|---|
| `getTeamNames()` | All 30 NBA teams — id, city, conference, division |
| `getPlayers()` | All active players with team IDs (paginated) |
| `getGamesForSeason(season)` | All games for a given season (default `2025`) |
| `getAllGameStats(gamesDf)` | Per-player box scores for every game — used for initial CSV export only |

### `load_layer.py`

Accepts JSON strings or CSV data and upserts into PostgreSQL. All writes use `INSERT ... ON CONFLICT DO UPDATE` so re-runs update existing rows instead of failing.

| Function | Table |
|---|---|
| `writeTeamsListToDB(teams)` | `teams` |
| `writePlayersListToDB(players)` | `players` |
| `writeGamesListToDB(gamesList)` | `games` |
| `writeGameStatsToDB(gameStats)` | `game_stats` |
| `loadGameStatsINTIAL()` | `game_stats` — loads from `game_stats.csv` due to API rate limits |

### `initial_load_dag.py`

Airflow DAG that runs the full initial load. Tasks execute in dependency order to respect FK constraints:

```
getTeamsNamesTask → loadTeamNamesTask ──┬──► loadPlayersTask ──┐
getPlayersTask ───────────────────────────┘                     ├──► loadInitialGameStats
getSeasonGamesTask → loadGamesListTask ────────────────────────┘
                     (waits for teams)
```

## Database Schema

| Table | PK | FK dependencies |
|---|---|---|
| `teams` | `id` | — |
| `players` | `id` | `teams(id)` |
| `games` | `game_id` | `teams(id)` |
| `game_stats` | `id` | `teams(id)`, `games(game_id)` |

Schema files are in `./sql/` and run automatically on first container start.

## Data

- `teams.csv` — 30 NBA teams
- `players.csv` — ~530 active players
- `games.csv` — 2025 season games
- `game_stats.csv` — ~7,700 rows of player box score stats (pre-exported due to rate limits)

## Setup

### 1. Environment variables

Create a `.env` file in the project root:

```
AUTH_KEY=your_balldontlie_api_key
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
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

Starts PostgreSQL on port `5332` and runs schema files from `./sql/` automatically.

### 4. Run Airflow

```bash
AIRFLOW__CORE__DAGS_FOLDER=$(pwd) airflow standalone
```

Then trigger the `game_data_init` DAG from the Airflow UI.

### Connecting to the database

```bash
docker exec -it postgres-game-data psql -U <POSTGRES_USER> -d game_data
```

## Resetting the database

```bash
docker compose down -v
docker compose up -d
```

The `-v` flag removes the volume so Postgres reinitializes and re-runs the schema files from scratch. To clear data without dropping the schema:

```sql
TRUNCATE TABLE game_stats, games, players, teams CASCADE;
```
