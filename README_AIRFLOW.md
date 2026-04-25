# Airflow Setup

This project uses Apache Airflow to orchestrate the NBA data pipeline.

## Running Airflow

Run Airflow locally using the current directory as the DAGs folder:

```bash
AIRFLOW__CORE__DAGS_FOLDER=$(pwd) airflow standalone
```

This starts the scheduler, webserver, and triggerer in one process. The UI is available at `http://localhost:8080`.

## DAG: `game_data_init`

Located in `initial_load_dag.py`. Performs the full initial load of all tables.

### Task execution order

```
getTeamsNamesTask → loadTeamNamesTask ──┬──► loadPlayersTask ──┐
getPlayersTask ───────────────────────────┘                     ├──► loadInitialGameStats
getSeasonGamesTask → loadGamesListTask ────────────────────────┘
                     (waits for teams)
```

The three extract tasks run in parallel. Load tasks are sequenced to respect FK constraints — teams must be loaded before players or games, and both must be loaded before game stats.

### Triggering the DAG

Trigger manually from the Airflow UI or via CLI:

```bash
airflow dags trigger game_data_init
```

## Notes

- The DAG has `schedule=None` — it only runs when triggered manually
- `catchup=False` — no backfill runs for past dates
- Inter-task data is passed as JSON strings (`orient='records'`) through XComs — no custom XCom backend needed
- `load_layer.py` manages its own database connection via env vars — no Airflow Postgres connection needs to be configured in the UI
