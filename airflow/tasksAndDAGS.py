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



##### TASKS ####

# DAG initialization
dag = DAG(
    'forecasting',
    default_args=default_args,
    description="Puesta en marcha de un servicio de predicción de humedad y temperatura",
    schedule_interval=None,
)


# Prepare work directory
PrepareWorkdir = BashOperator(
    task_id='prepare_workdir',
    bash_command= 'mkdir -p /tmp/workflow/ && mkdir -p /tmp/workflow/v1 && mkdir -p /tmp/workflow/v2 ',
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
    task_id='download_mongo_container',
    bash_command="docker pull mongo:latest",
    dag=dag,
)

# Run MongoDB container: option -d (detached mode)
RunMongo = BashOperator(
    task_id='create_mongo_container',
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

# Import data to mongoDB container 
ImportDataToMongoDB = PythonOperator(
    task_id='import_data_to_mongoDB',
    provide_context=True,
    python_callable=functions.importData,
    op_kwargs={
        'data': '/tmp/workflow/data.csv',
    },
    dag=dag,
)

# Train model with temperature data
trainArimaTemp = PythonOperator(
    task_id='train_arima_model_temperature',
    provide_context=True,
    python_callable=functions.trainArimaTEMP,
    op_kwargs={
        'data': '/tmp/workflow/arimaTemp.pkl',
    },
    dag=dag,
)

# Train model with humidity data
trainArimaHum = PythonOperator(
    task_id='train_arima_model_humidity',
    provide_context=True,
    python_callable=functions.trainArimaHUM,
    op_kwargs={
        'data': '/tmp/workflow/arimaHum.pkl',
    },
    dag=dag,
)


downloadMicroserviceV1 = BashOperator(
    task_id='download_microservice_v1',
    bash_command=f'''curl -o /tmp/workflow/v1/Dockerfile https://raw.githubusercontent.com/pabloluque14/Airflow_Prediction/master/src/v1/Dockerfile;
                    curl -o /tmp/workflow/v1/requirements.txt https://raw.githubusercontent.com/pabloluque14/Airflow_Prediction/master/src/v1/requirements.txt;
                    curl -o /tmp/workflow/v1/microservice_v1.py https://raw.githubusercontent.com/pabloluque14/Airflow_Prediction/master/src/v1/microservice_v1.py;
                    curl -o /tmp/workflow/v1/test.py https://raw.githubusercontent.com/pabloluque14/Airflow_Prediction/master/src/v1/test.py;''',
    dag=dag,
)


runV1Test = BashOperator(
    task_id='run_v1_test',
    depends_on_past= True,
    bash_command='python3 /tmp/workflow/v1/test.py',
    dag=dag,
)

createV1Image = BashOperator(
    task_id='create_v1_image',
    bash_command='docker build /tmp/workflow/v1 -t microservice_v1',
    dag=dag,
)


deployMicroserviceV1 = BashOperator(
    task_id='deploy_microservice_v1',
    bash_command='docker run --detach -p 80:5000 microservice_v1',
    dag=dag,
)


PrepareWorkdir >> takeDataA >> unzipDataA >> MergeData
PrepareWorkdir >> takeDataB >> unzipDataB >> MergeData
PrepareWorkdir >> DonwloadMongo >> RunMongo
[MergeData, RunMongo] >> ImportDataToMongoDB

ImportDataToMongoDB >> trainArimaTemp
ImportDataToMongoDB >> trainArimaHum


