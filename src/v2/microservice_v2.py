from flask import Flask
from flask import request
from flask import Response

import pandas as pd
import pmdarima as pm
import numpy as np

#from bson import json_util
import json

from statsmodels.tsa.arima_model import ARIMA
from datetime import datetime, timedelta, date

import pickle


app = Flask(__name__)


@app.route('/servicio/v2/<int:n>horas/', methods=['GET'])
def getForecastingV1(n):
    
    # localhost path: /tmp/workflow/v2/ docker path: ./
    result = completeModel(n, './smoothHum.pkl', './smoothTemp.pkl')
    return Response(json.dumps(result), status=200, mimetype="application/json")


def getNdaysList(n):
    dayList = list()
    for i in range(n):
        today = datetime.today() 
        days = timedelta(hours=i)
        tomorrow = today + days
        final= str(tomorrow.year)+ "-"+str(tomorrow.month)+ "-"+ str(tomorrow.day)+ " " + str(tomorrow.hour) + ":" + str(tomorrow.minute)
        dayList.append(final)
    return dayList 

def forecastToDictionary(n, tempForecast, humForecast):
    days = list()
    days = getNdaysList(n)
    temp = list(tempForecast)
    hum = list(humForecast)
    
    total = list()
    for i in range(len(days)):
        
        dic = {'hour' : days[i], 'temp' : temp[i], 'hum': hum[i] }
        total.append(dic)
    
    return total


def getModel(path):
    # open the .pkl model 
    with open(path, 'rb') as file:
        model = pickle.load(file)
    return model

def forecast(model, n):
    # Forecast
    fc = model.predict(24, 23+n)
    # fc contains the forecasting for the next 24 hours.
    return fc

def completeModel(n,HumModelPath, tempModelPath):
    
    temp_model = getModel(tempModelPath)
    hum_model = getModel(HumModelPath)

    tempForecast = forecast(temp_model, n)
    humForecast = forecast(hum_model, n)

    dic = forecastToDictionary(n, tempForecast, humForecast)
    
    return dic
