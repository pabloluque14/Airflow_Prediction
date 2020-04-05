# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 00:20:34 2020

@author: pabloluque
"""
import pandas as pd
import os.path
import pymongo
from pymongo import MongoClient



def mergeData(**kwargs):

    df_humidity = pd.read_csv(kwargs['hum_file'], sep=',')
    df_temperature = pd.read_csv(kwargs['temp_file'], sep=',')


    humidity = df_humidity['San Francisco']
    date = list(df_humidity['datetime'])
    temperature = df_temperature['San Francisco']

    df = pd.DataFrame(date, columns = ['date'])


    df = df.join(humidity)

    df = df.join(temperature, lsuffix = ' temperature')

    df.columns=['DATE','TEMP', 'HUM']

    df.to_csv("/tmp/workflow/data.csv", encoding='utf8', index=False, sep=";")


def importData(**kwargs):
    
    client = MongoClient('localhost', 28900)
    # database
    db = client["timePrediction"]
    # collection
    company= db["sanFrancisco"]

    # dont forget to use the right separation -> ;
    df = pd.read_csv("/tmp/workflow/data.csv", sep=';')
    data_dict = df.to_dict("records")
    company.insert_one({"index":"SanFrancisco","data":data_dict})



def exportData(**kwargs):

    client = MongoClient('localhost', 28900)
    # database
    db = client["timePrediction"]
    # collection
    company= db["sanFrancisco"]

    data_from_db = company.find_one({"index":"SanFrancisco"})
    df = pd.DataFrame(data_from_db["data"])

    # TODO: df para la prediccion del modelo
