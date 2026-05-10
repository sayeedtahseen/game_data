import json
import os
import pandas as pd
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.dialects.postgresql import insert as pg_insert

from airflow.hooks.base import BaseHook


def _get_engine(conn_id: str = "supabase_postgres"):
    conn = BaseHook.get_connection(conn_id)
    url = f"postgresql://{conn.login}:{conn.password}@{conn.host}:{conn.port}/{conn.schema}"
    return create_engine(url)


def _upsert(records, table_name, primary_key, conn_id: str = "supabase_postgres"):
    engine = _get_engine(conn_id)
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)
    with engine.begin() as conn:
        stmt = pg_insert(table).values(records)
        update_cols = {col: stmt.excluded[col] for col in records[0].keys() if col != primary_key}
        conn.execute(stmt.on_conflict_do_update(index_elements=[primary_key], set_=update_cols))


def writeTeamsListToDB(teams, conn_id: str = "supabase_postgres"):
    try:
        _upsert(json.loads(teams), 'teams', 'id', conn_id)
        print('Writing to teams table successful')
    except Exception as error:
        print("Error in writing teams to DB: ", error)
        raise


def writeGamesListToDB(gamesList, conn_id: str = "supabase_postgres"):
    try:
        _upsert(json.loads(gamesList), 'games', 'game_id', conn_id)
        print('Writing to games table successful')
    except Exception as error:
        print("Error in writing games to DB: ", error)
        raise


def writePlayersListToDB(players, conn_id: str = "supabase_postgres"):
    try:
        _upsert(json.loads(players), 'players', 'id', conn_id)
        print('Writing to players table successful')
    except Exception as error:
        print("Error in writing players to DB: ", error)
        raise


def writeGameStatsToDB(gameStats, conn_id: str = "supabase_postgres"):
    try:
        _upsert(json.loads(gameStats), 'game_stats', 'id', conn_id)
        print('Writing to game stats table successful')
    except Exception as error:
        print("Error in writing game_stats to DB: ", error)
        raise


def loadGameStatsINTIAL(conn_id: str = "supabase_postgres"):
    gameStatsDf = pd.read_csv('game_stats.csv', index_col=0)
    gameStatsDf.columns = gameStatsDf.columns.str.replace('.', '_', regex=False)
    try:
        _upsert(gameStatsDf.to_dict(orient='records'), 'game_stats', 'id', conn_id)
        print('Writing to game_stats table successful')
    except Exception as error:
        print("Error in writing game stats to DB: ", error)
        raise
