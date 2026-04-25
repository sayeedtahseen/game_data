import os
import pandas as pd;
import pprint;
import time
from dotenv import load_dotenv

load_dotenv();
API_KEY=os.getenv('AUTH_KEY');


from balldontlie import BalldontlieAPI
from balldontlie.exceptions import RateLimitError
api = BalldontlieAPI(api_key=API_KEY);


# Get all team names and ids
def getTeamNames():
  teamDf = None;
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
      });

    teamDf = pd.DataFrame(nbaTeamList);

    # drop entries that are not in nba
    teamDf.dropna(how='any', inplace=True); 

    print("Successfully retrieved players data");
    return teamDf;
  except Exception as error:
    print("Error retrieving teams: ", error);


# Gets list of active players, 
def getPlayers():
  playersDf = None;
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
    print("Successfully retrieved players data");

    return playersDf;
  except Exception as error:
    print("Error retriveing player: ", error)

# Get all games for current season
def getGamesForCurrentSeason():
  gamesDf;
  gamesList = []
  currentSeason = str(time.localtime().tm_year);
  nextCursor = None;
  kwargs = {
        'seasons': [currentSeason],
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

    print("Successfully retrieved games list data");
    return gamesDf;
  except Exception as error:
    print("Error retrieving games list: ", error);


# Get game stats for each player, for initial load
def getAllGameStats(gamesDf):
  allStatsDf = None;

  if gamesDf is None:
    raise "No games list";
  
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

    print("Successfully retrieved all games stats");
    return allStatsDf;

  except Exception as error:
    print('Error retrieving game stats: ', error);
    if not allStatsDf.empty:
      print(f'Partial data saved: {len(allStatsDf)} rows written to game_stats.csv');
      return allStatsDf;
