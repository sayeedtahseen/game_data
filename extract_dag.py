import pendulum
from airflow.sdk import dag, task;

from extract import readTeamListCSV;
@dag(
  schedule = None,
  start_date=pendulum.datetime(2026, 4, 24, tz="UTC"),
  catchup=False,
  tags=['extract', 'game_data']
)
def extract_dag_taskflow():
  """
  This is a DAG for the extract function to retrieve game data
  """
  @task()
  def extract():
    return readTeamListCSV();

  readCSVData = extract();
  
extract_dag = extract_dag_taskflow();