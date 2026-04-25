import pendulum
from airflow.sdk import dag, task;

from extract_layer import getTeamNames, getPlayers, getGamesForSeason
from load_layer import writeTeamsListToDB, writePlayersListToDB, writeGamesListToDB, loadGameStatsINTIAL
@dag(
  schedule = None,
  start_date=pendulum.datetime(2026, 4, 24, tz="UTC"),
  catchup=False,
  tags=['game_data']
)
def game_data_init():
  """
  This is a DAG for the extract function to retrieve game data
  """
  @task()
  def getTeamsNamesTask():
    return getTeamNames();

  @task()
  def loadTeamNamesTask(teamNamesList):
    writeTeamsListToDB(teamNamesList);

  @task()
  def getPlayersTask():
    return getPlayers;
  
  @task()
  def loadPlayersTask(players):
    writePlayersListToDB(players);

  @task()
  def getSeasonGamesTask():
    return getGamesForSeason();

  @task()
  def loadGamesListTask(gamesList):
    writeGamesListToDB(gamesList);

  @taks()
  def loadInitialGameStats():
    loadGameStatsINTIAL();

  teamNames = getTeamsNamesTask();
  loadTeamNamesTask(teamNames);

  playersList = getPlayersTask();
  loadPlayersTask(playersList);

  gamesList = getSeasonGamesTask();
  loadGamesListTask(gamesList);

  loadInitialGameStats();

game_data_init();