# Database Setup

This project uses a PostgreSQL database running in Docker. The schema is split across 4 SQL files in the `./sql` directory that are automatically run on first container startup.

## Running the Database

```bash
docker compose up -d
```

To reset the database from scratch (re-runs all init scripts):

```bash
docker compose down -v
docker compose up -d
```

The `-v` flag removes the volume so Postgres reinitializes and re-runs the SQL files.

## Connection Details

| Setting | Value |
|---|---|
| Host | `localhost` |
| Port | `5332` |
| User | `POSTGRES_USER` from `.env` |
| Password | `POSTGRES_PASSWORD` from `.env` |
| Database | `POSTGRES_DB` from `.env` |

Connect via psql:
```bash
docker exec -it postgres-game-data psql -U <POSTGRES_USER> -d game_data
```

## Schema

### `01_teams.sql`
Stores all 30 NBA teams. No foreign key dependencies — runs first.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key |
| `conference` | VARCHAR(10) | East or West |
| `division` | VARCHAR(20) | Division name |
| `city` | VARCHAR(50) | Team city |
| `name` | VARCHAR(50) | Team name |
| `full_name` | VARCHAR(100) | Full team name |
| `abbreviation` | VARCHAR(5) | 3-letter abbreviation |

---

### `02_players.sql`
Stores all active NBA players. References `teams`.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key |
| `first_name` | VARCHAR(100) | Player first name |
| `last_name` | VARCHAR(100) | Player last name |
| `team_id` | INTEGER | Foreign key → `teams.id` |

---

### `03_games.sql`
Stores all games for the current season. References `teams` for both home and visitor.

| Column | Type | Description |
|---|---|---|
| `game_id` | INTEGER | Primary key |
| `date` | DATE | Game date |
| `season` | INTEGER | Season year |
| `status` | VARCHAR(50) | Game status |
| `period` | INTEGER | Current period |
| `time` | VARCHAR(20) | Time remaining |
| `postseason` | BOOLEAN | Playoff game flag |
| `home_team_score` | INTEGER | Home team score |
| `visitor_team_score` | INTEGER | Visitor team score |
| `home_team_id` | INTEGER | Foreign key → `teams.id` |
| `home_team_name` | VARCHAR(50) | Home team name |
| `home_team_abb` | VARCHAR(5) | Home team abbreviation |
| `visitor_team_id` | INTEGER | Foreign key → `teams.id` |
| `visitor_team_name` | VARCHAR(50) | Visitor team name |
| `visitor_team_abb` | VARCHAR(5) | Visitor team abbreviation |

---

### `04_game_stats.sql`
Stores per-player box score stats for every game. References `players`, `teams`, and `games`.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key |
| `min` | INTEGER | Minutes played |
| `fgm` | NUMERIC | Field goals made |
| `fga` | NUMERIC | Field goals attempted |
| `fg_pct` | NUMERIC | Field goal percentage |
| `fg3m` | NUMERIC | 3-pointers made |
| `fg3a` | NUMERIC | 3-pointers attempted |
| `fg3_pct` | NUMERIC | 3-point percentage |
| `ftm` | NUMERIC | Free throws made |
| `fta` | NUMERIC | Free throws attempted |
| `ft_pct` | NUMERIC | Free throw percentage |
| `oreb` | NUMERIC | Offensive rebounds |
| `dreb` | NUMERIC | Defensive rebounds |
| `reb` | NUMERIC | Total rebounds |
| `ast` | NUMERIC | Assists |
| `stl` | NUMERIC | Steals |
| `blk` | NUMERIC | Blocks |
| `turnover` | NUMERIC | Turnovers |
| `pf` | NUMERIC | Personal fouls |
| `pts` | NUMERIC | Points |
| `player_id` | INTEGER | Player id (no FK constraint) |
| `player_first_name` | VARCHAR(100) | Player first name |
| `player_last_name` | VARCHAR(100) | Player last name |
| `player_team_id` | INTEGER | Foreign key → `teams.id` |
| `game_id` | INTEGER | Foreign key → `games.game_id` |
| `game_date` | DATE | Game date |
| `game_season` | INTEGER | Season year |
| `game_postseason` | BOOLEAN | Playoff game flag |
| `home_team_score` | INTEGER | Home team score |
| `visitor_team_score` | INTEGER | Visitor team score |
| `home_team_id` | INTEGER | Foreign key → `teams.id` |
| `visitor_team_id` | INTEGER | Foreign key → `teams.id` |

---

## Foreign Key Dependencies

```
teams
  ├── players.team_id
  ├── games.home_team_id
  ├── games.visitor_team_id
  └── game_stats.player_team_id
            .game_home_team_id
            .game_visitor_team_id

games
  └── game_stats.game_id
```

Files are numbered `01`–`04` so Docker runs them in the correct order — referenced tables must exist before the tables that depend on them.

> **Note:** When replacing the `games` table, drop it with `CASCADE` first to avoid foreign key conflicts with `game_stats`:
> ```python
> conn.execute(text("DROP TABLE IF EXISTS games CASCADE"))
> ```
