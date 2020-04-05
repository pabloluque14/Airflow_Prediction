# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 00:20:34 2020

@author: pabloluque
"""

from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import requests

import functions



# Default arguments
default_args = {
    'owner': 'Pablo Luque Moreno',
    'depends_on_past': False,
    #Start Date: two days ago
    'start_date': days_ago(2),
    'email': ['pabloluque13@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    #'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}



base_dir='tmp/workflow'

##### TASKS ####

# DAG initialization
dag = DAG(
    'predictions_service',
    default_args=default_args,
    description="Puesta en marcha de un servicio de predicción de humedad y temperatura",
    schedule_interval=None,
)


# Prepare work directory
PrepareWorkdir = BashOperator(
    task_id='prepare_workdir',
    bash_command= 'mkdir -p /tmp/workflow/',
    dag=dag,
)

# Important: change url from github in the case of download the dat from tha site
# Download humidity data
takeDataA = BashOperator(
    task_id='takeDataA',
    bash_command='curl -o /tmp/workflow/humidity.csv.zip https://raw.githubusercontent.com/manuparra/MaterialCC2020/master/humidity.csv.zip',
    dag=dag
)

# Download temperature data
takeDataB = BashOperator(
    task_id='takeDataB',
    bash_command='curl -o /tmp/workflow/temperature.csv.zip https://raw.githubusercontent.com/manuparra/MaterialCC2020/master/temperature.csv.zip',
    dag=dag
)


# Unzip dat file humidity
unzipDataA = BashOperator(
    task_id='unzip_humidity_data',
    depends_on_past=True,
    bash_command='unzip -od /tmp/workflow/ /tmp/workflow/humidity.csv.zip',
    dag=dag,
)

# Unzip dat file temperature
unzipDataB = BashOperator(
    task_id='unzip_temperature_data',
    depends_on_past=True,
    bash_command='unzip -od /tmp/workflow/ /tmp/workflow/temperature.csv.zip',
    dag=dag,
)


# Merge temperature and humidity datasets and create data file
MergeData = PythonOperator(
    task_id='merge_data',
    provide_context=True,
    python_callable=functions.mergeData,
    op_kwargs={
        'temp_file': '/tmp/workflow/temperature.csv',
        'hum_file': '/tmp/workflow/humidity.csv',
    },
    dag=dag,
)


# Download MongoDB image
DonwloadMongo = BashOperator(
    task_id='descargar_imagen_Mongo',
    bash_command="docker pull mongo:latest",
    dag=dag,
)

# Run MongoDB container: option -d (detached mode)
RunMongo = BashOperator(
    task_id='crear_contenedor_Mongo',
    depends_on_past=True,
    bash_command="docker run --name mongoDBAirflow -d -p 28900:27017 mongo:latest",
    dag=dag,
)


#Import the data file to mongoDB : You should have installed mongo tools 
"""
options : 
    --drop (drop db if already exist)
    --headerline (if the csv file has a first line to put the columns names)
"""
"""
ImportDataToMongoDB = BashOperator(
    task_id='import_data_to_mongoDB',
    depends_on_past=True,
    bash_command="docker exec mongoDBAirflow mongoimport --db sanFrancisco --collection TimePrediction --file /tmp/workflow/data.csv --type csv --drop --port 28900 --headerline --host localhost",
    dag=dag,
)
"""
"""
# Export the data file from mongoDB
ExportarDatosBD = BashOperator(
    task_id='export_data_to_mongoDB',
    depends_on_past=True,
    bash_command="docker exec mongoDBAirflow mongoexport --db sanFrancisco --collection TimePrediction --out /tmp/workflow/mongo_dataset.csv --forceTableScan  --port 28900 --host localhost --type csv -f DATE,HUM,TEMP",
    dag=dag,
)
"""


ImportDataToMongoDB = PythonOperator(
    task_id='import_data_to_mongoDB',
    provide_context=True,
    python_callable=functions.importData,
    op_kwargs={
        'data': '/tmp/workflow/data.csv',
    },
    dag=dag,
)

PrepareWorkdir >> takeDataA >> unzipDataA >> MergeData
PrepareWorkdir >> takeDataB >> unzipDataB >> MergeData
PrepareWorkdir >> DonwloadMongo >> RunMongo
[MergeData, RunMongo] >> ImportDataToMongoDB

