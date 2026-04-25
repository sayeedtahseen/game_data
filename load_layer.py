import json
import os
import pandas as pd
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.dialects.postgresql import insert as pg_insert

from dotenv import load_dotenv
load_dotenv();

# engine for postgres
engine = create_engine(
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5332/{os.getenv('POSTGRES_DB')}"
)

def _upsert(records, table_name, primary_key):
  metadata = MetaData()
  table = Table(table_name, metadata, autoload_with=engine)
  with engine.begin() as conn:
    stmt = pg_insert(table).values(records)
    update_cols = {col: stmt.excluded[col] for col in records[0].keys() if col != primary_key}
    conn.execute(stmt.on_conflict_do_update(index_elements=[primary_key], set_=update_cols))

def writeTeamsListToDB(teams):
  try:
    _upsert(json.loads(teams), 'teams', 'id')
    print('Writing to teams table successful');
  except Exception as error:
    print("Error in writing teams to DB: ", error);
    raise;

def writeGamesListToDB(gamesList):
  try:
    _upsert(json.loads(gamesList), 'games', 'game_id')
    print('Writing to games table successful');
  except Exception as error:
    print("Error in writing games to DB: ", error);
    raise;

def writePlayersListToDB(players):
  try:
    _upsert(json.loads(players), 'players', 'id')
    print('Writing to players table successful');
  except Exception as error:
    print("Error in writing players to DB: ", error);
    raise;

def writeGameStatsToDB(gameStats):
  try:
    _upsert(json.loads(gameStats), 'game_stats', 'id')
    print('Writing to game stats table successful');
  except Exception as error:
    print("Error in writing game_stats to DB: ", error);
    raise;

# INITIAL LOAD TO GAME STATS, because of rate limiting
def loadGameStatsINTIAL():
  gameStatsDf = pd.read_csv('game_stats.csv', index_col=0);
  gameStatsDf.columns = gameStatsDf.columns.str.replace('.', '_', regex=False);
  try:
    _upsert(gameStatsDf.to_dict(orient='records'), 'game_stats', 'id')
    print('Writing to players game_stats successful');
  except Exception as error:
    print("Error in writing game stats to DB: ", error);
    raise;
