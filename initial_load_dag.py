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
    return getPlayers();
  
  @task()
  def loadPlayersTask(players):
    writePlayersListToDB(players);

  @task()
  def getSeasonGamesTask():
    return getGamesForSeason();

  @task()
  def loadGamesListTask(gamesList):
    writeGamesListToDB(gamesList);

  @task()
  def loadInitialGameStats():
    loadGameStatsINTIAL();

  teamNames = getTeamsNamesTask()
  loadedTeams = loadTeamNamesTask(teamNames)

  playersList = getPlayersTask()
  loadedPlayers = loadPlayersTask(playersList)
  loadedTeams >> loadedPlayers

  gamesList = getSeasonGamesTask()
  loadedGames = loadGamesListTask(gamesList)
  loadedTeams >> loadedGames

  loadedStats = loadInitialGameStats()
  [loadedPlayers, loadedGames] >> loadedStats

game_data_init();