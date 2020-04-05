# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 00:20:34 2020

@author: pabloluque
"""
import pandas as pd
import os.path


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
