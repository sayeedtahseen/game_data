import os
import pandas as pd
from sqlalchemy import create_engine

# engine for postgres
engine = create_engine(
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5332/{os.getenv('POSTGRES_DB')}"
)

def writeTeamsListToDB(teamsDf):
  try:
    teamsDf.to_sql("teams", engine, if_exists='append', index=False);
    print('Writing to teams table successful');
  except Exception as error:
    print("Error in writing teams to DB: ", error);

def writeGamesListToDB(gamesListDf):
  try:
    gamesListDf.to_sql("games", engine, if_exists='append', index=False);
    print('Writing to games table successful');
  except Exception as error:
    print("Error in writing games to DB: ", error);

def writePlayersListToDB(playersDf):
  try:
    playersDf.to_sql("players", engine, if_exists='append', index=False);
    print('Writing to players table successful');
  except Exception as error:
    print("Error in writing players to DB: ", error);

def writeGameStatsToDB(gameStatsDf):
  try:
    gameStatsDf.to_sql("game_stats", engine, if_exists='append', index=False);
    print('Writing to game stats table successful');
  except Exception as error:
    print("Error in writing game_stats to DB: ", error);

# INITIAL LOAD TO GAME STATS, because of rate limiting 
def loadGameStatsINTIAL():
  gameStatsDf = pd.read_csv('game_stats.csv');
  try:
    gameStatsDf.to_sql("game_stats", engine, if_exists='append', index=False);
    print('Writing to players game_stats successful');
  except Exception as error:
    print("Error in writing game stats to DB: ", error);

