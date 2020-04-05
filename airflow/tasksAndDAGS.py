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

# Inluir biliotecas PIP



#Default arguments
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

#Inicialización del grafo DAG de tareas para el flujo de trabajo

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
    depends_on_past=False,
    bash_command='curl -o /tmp/workflow/humidity.csv.zip https://raw.githubusercontent.com/manuparra/MaterialCC2020/master/humidity.csv.zip',
    dag=dag
)

# Download temperature data
takeDataB = BashOperator(
    task_id='takeDataB',
    depends_on_past=False,
    bash_command='curl -o /tmp/workflow/temperature.csv.zip https://raw.githubusercontent.com/manuparra/MaterialCC2020/master/temperature.csv.zip',
    dag=dag
)


# Unzip dat files
unzipDataA = BashOperator(
    task_id='unzip_humidity_data',
    depends_on_past=True,
    bash_command='unzip -od /tmp/workflow/ /tmp/workflow/humidity.csv.zip',
    dag=dag,
)


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


PrepareWorkdir >> takeDataA >> unzipDataA >> MergeData
PrepareWorkdir >> takeDataB >> unzipDataB >> MergeData
