import os
import pandas as pd;
from sqlalchemy import create_engine
import pprint;
import time
from dotenv import load_dotenv

load_dotenv();
API_KEY=os.getenv('AUTH_KEY');
engine = create_engine(
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5332/{os.getenv('POSTGRES_DB')}"
)


from balldontlie import BalldontlieAPI
from balldontlie.exceptions import RateLimitError
api = BalldontlieAPI(api_key=API_KEY);

teamDf = None;
playersDf = None;
gamesDf = None;
allStatsDf = None;

# Get all team names and ids
# To be queried later
def getTeamNames():
  global teamDf;
  nbaTeamList = []
  try:
    teams = api.nba.teams.list().data;
    for team in teams:
      nbaTeamList.append( {
        'id': team.id,
        'conference': team.conference,
        'division': team.division,
        'city': team.city, 
        'name': team.name, 
        'full_name':  team.full_name, 
        'abbreviation':  team.abbreviation
      })
    teamDf = pd.DataFrame(nbaTeamList);
    # drop entries that are not in nba
    teamDf.dropna(how='any', inplace=True); 
    teamDf.to_csv('teams.csv');
    print("Successfully retrieved teams data");
  except Exception as error:
    print("Error retrieving teams: ", error);
    

  # pprint.pprint(nbaTeamList);

# Gets list of active players, 
def getPlayers():
  global playersDf;
  nextCursor = None
  nbaPlayers = []
  try:
    while True:
      kwargs = {'per_page': 100}
      if nextCursor:
        kwargs['cursor'] = nextCursor
      response = api.nba.players.list_active(**kwargs)
      
      meta = response.meta;
      players = response.data;

      for player in players:
        nbaPlayers.append({
          'id': player.id,
          'first_name': player.first_name,
          'last_name': player.last_name,
          'team_id': player.team.id
        })
      
      # print(meta)
      if not meta.next_cursor:
        break;
      nextCursor = meta.next_cursor;

      time.sleep(1.5);
    
    playersDf = pd.DataFrame(nbaPlayers);
    playersDf.to_csv('players.csv');
    print("Successfully retrieved players data");
  except Exception as error:
    print("Error retriveing player: ", error)

# Get all games for current season
def getGamesForCurrentSeason():
  global gamesDf;
  gamesList = []
  nextCursor = None;
  kwargs = {
        'seasons': ['2025'],
        'per_page': 100
        };
  try:
    while True:
      if nextCursor: 
        kwargs['cursor'] = nextCursor;
      
      response = api.nba.games.list(**kwargs);

      for game in response.data:
        gamesList.append({
        'game_id': game.id,
        'date': game.date,
        'season': game.season,
        "status": game.status,
        "period": game.period,
        "time": game.time,
        "postseason": game.postseason,
        "home_team_score": game.home_team_score,
        "visitor_team_score": game.visitor_team_score,
        "home_team_id": game.home_team.id,
        "home_team_name": game.home_team.name,
        "home_team_abb": game.home_team.abbreviation,
        "visitor_team_id": game.visitor_team.id,
        "visitor_team_name": game.visitor_team.name,
        "visitor_team_abb": game.visitor_team.abbreviation
    })

      meta = response.meta;
      if not meta.next_cursor:
        break;
      nextCursor = meta.next_cursor;
      time.sleep(1.5);

    gamesDf = pd.DataFrame(gamesList);
    gamesDf.to_csv('games.csv');
    print("Successfully retrieved games list data");
  except Exception as error:
    print("Error retrieving games list: ", error);

# Get game stats for each player, for initial load
def getAllGameStats():
  global gamesDf;
  global allStatsDf;
  if gamesDf is None:
    print("Getting games list from DB");
    gamesDf = pd.read_csv('games.csv');
  gameList = gamesDf['game_id'].to_list();
    
  nextCursor = None;
  kwargs = {
        'per_page': 100
        };

  allStats = pd.DataFrame();
  try:
    for index, gameId in enumerate(gameList):
      retries = 0
      while True:
        try:
          response = api.nba.stats.list(game_ids=[gameId], per_page=100).data;
          break;
        except Exception as e:
          if isinstance(e, RateLimitError) and retries < 3:
            retries += 1;
            print(f'Rate limited, retrying in {retries * 15}s...');
            time.sleep(retries * 15);
          else:
            print(f'Failed at index {index}, game_id {gameId}');
            raise;

      data_as_dicts = [item.model_dump() for item in response];
      statsDF = pd.json_normalize(data_as_dicts);
      statsDF.drop(columns=[
        'player.position',
        'player.height',
        'player.weight',
        'player.jersey_number',
        'player.college',
        'player.country',
        'player.draft_year',
        'player.draft_round',
        'player.draft_number',
        'player.team',
        'team.id',
        'team.conference',
        'team.division',
        'team.city',
        'team.name',
        'team.full_name',
        'team.abbreviation',
        'game.status',
        'game.period',
        'game.time',
        'game.home_team',
        'game.visitor_team'],
        inplace=True);

      allStatsDf = pd.concat([allStatsDf, statsDF], ignore_index=True);
      time.sleep(1.1);

    allStatsDf.to_csv('game_stats.csv', mode='a', index=False, header=False);

  except Exception as error:
    print('Error retrieving game stats: ', error);
    if not allStatsDf.empty:
      allStatsDf.to_csv('game_stats.csv');
      print(f'Partial data saved: {len(allStatsDf)} rows written to game_stats.csv');


# teams list read for inital load, and insert into teams table
def readTeamListCSV():
  global teamDf;
  print('Reading teams list...')
  try:
    teamDf = pd.read_csv('teams.csv', index_col=0);
    teamDf.dropna(how='any', inplace=True);
  except Exception as error:
    print("Error reading data from CSV for teams", error);

  try:
    teamDf.to_sql("teams", engine, if_exists='append', index=False);
    print('Writing to teams table successful');
  except Exception as error:
    print("Error in writing teams to DB: ", error);
  
  

# games list read for inital load, and insert into games table
def readGamesListCSV():
  global gamesDf;
  print('Reading games list...')
  
  try:
    gamesDf = pd.read_csv('games.csv', index_col=0);
  except Exception as error:
    print("Error reading data from CSV for games: ", error);

  try:
    gamesDf.to_sql("games", engine, if_exists='append', index=False);
    print('Writing to games table successful');
  except Exception as error:
    print("Error in writing games to DB: ", error);
  


if __name__ == "__main__":
  print("Starting Extract");
  readTeamListCSV()
