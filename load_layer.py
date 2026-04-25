import io
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

def _upsert(df, table_name, primary_key):
  metadata = MetaData()
  table = Table(table_name, metadata, autoload_with=engine)
  records = df.to_dict(orient='records')
  with engine.begin() as conn:
    stmt = pg_insert(table).values(records)
    update_cols = {col: stmt.excluded[col] for col in df.columns if col != primary_key}
    conn.execute(stmt.on_conflict_do_update(index_elements=[primary_key], set_=update_cols))

def writeTeamsListToDB(teams):
  try:
    teamsDf = pd.read_json(io.StringIO(teams));
    _upsert(teamsDf, 'teams', 'id')
    print('Writing to teams table successful');
  except Exception as error:
    print("Error in writing teams to DB: ", error);
    raise;

def writeGamesListToDB(gamesList):
  try:
    gamesListDf = pd.read_json(io.StringIO(gamesList));
    _upsert(gamesListDf, 'games', 'game_id')
    print('Writing to games table successful');
  except Exception as error:
    print("Error in writing games to DB: ", error);
    raise;

def writePlayersListToDB(players):
  try:
    playersDf = pd.read_json(io.StringIO(players));
    _upsert(playersDf, 'players', 'id')
    print('Writing to players table successful');
  except Exception as error:
    print("Error in writing players to DB: ", error);
    raise;

def writeGameStatsToDB(gameStats):
  try:
    gameStatsDf = pd.read_json(io.StringIO(gameStats));
    _upsert(gameStatsDf, 'game_stats', 'id')
    print('Writing to game stats table successful');
  except Exception as error:
    print("Error in writing game_stats to DB: ", error);
    raise;

# INITIAL LOAD TO GAME STATS, because of rate limiting
def loadGameStatsINTIAL():
  gameStatsDf = pd.read_csv('game_stats.csv', index_col=0);
  gameStatsDf.columns = gameStatsDf.columns.str.replace('.', '_', regex=False);
  try:
    _upsert(gameStatsDf, 'game_stats', 'id')
    print('Writing to players game_stats successful');
  except Exception as error:
    print("Error in writing game stats to DB: ", error);
    raise;
