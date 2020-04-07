# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 00:20:34 2020

@author: pabloluque
"""
import pandas as pd
import os.path
import pymongo
from pymongo import MongoClient
import pmdarima as pm
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
import pickle



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



def exportData():

    client = MongoClient('localhost', 28900)
    # database
    db = client["timePrediction"]
    # collection
    company= db["sanFrancisco"]

    data_from_db = company.find_one({"index":"SanFrancisco"})
    df = pd.DataFrame(data_from_db["data"])

    return df

    

def trainArimaTEMP(**kwargs):

    if os.path.isfile(kwargs['data']):
        return

    df=exportData()

    # delete NaN values for the model
    df = df.dropna()

    model = pm.auto_arima(df['TEMP'], start_p=1, start_q=1,
                        test='adf',       # use adftest to find optimal 'd'
                        max_p=3, max_q=3, # maximum p and q
                        m=1,              # frequency of series
                        d=None,           # let model determine 'd'
                        seasonal=False,   # No Seasonality
                        start_P=0, 
                        D=0, 
                        trace=True,
                        error_action='ignore',  
                        suppress_warnings=True, 
                        stepwise=True)

    with open(kwargs['data'], 'wb') as file:
        pickle.dump(model, file)


def trainArimaHUM(**kwargs):

    if os.path.isfile(kwargs['data']):
        return

    df=exportData()

    # delete NaN values for the model
    df = df.dropna()

    model = pm.auto_arima(df['HUM'], start_p=1, start_q=1,
                        test='adf',       # use adftest to find optimal 'd'
                        max_p=3, max_q=3, # maximum p and q
                        m=1,              # frequency of series
                        d=None,           # let model determine 'd'
                        seasonal=False,   # No Seasonality
                        start_P=0, 
                        D=0, 
                        trace=True,
                        error_action='ignore',  
                        suppress_warnings=True, 
                        stepwise=True)


    # Forecast
    #n_periods = 24 # One day
    #fc, confint = model.predict(n_periods=n_periods, return_conf_int=True)

    with open(kwargs['data'], 'wb') as file:
        pickle.dump(model, file)


def trainSmoothHUM(**kwargs):

    if os.path.isfile(kwargs['data']):
        return

    df=exportData()

    # delete NaN values for the model
    df = df.dropna()

    model = SimpleExpSmoothing(df['HUM']).fit()

    with open(kwargs['data'], 'wb') as file:
        pickle.dump(model, file)


def trainSmoothTEMP(**kwargs):

    if os.path.isfile(kwargs['data']):
        return

    df=exportData()

    # delete NaN values for the model
    df = df.dropna()

    model = SimpleExpSmoothing(df['TEMP']).fit()

    with open(kwargs['data'], 'wb') as file:
        pickle.dump(model, file)

