from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
from pyspark.sql import SparkSession
from pyspark.sql import DataFrameReader
from urllib.request import urlopen
from pymongo import MongoClient
from prophet import Prophet
from datetime import date
import pandas as pd
import requests
import pymongo
import json
import re
import os

app = Flask(__name__)# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

client = MongoClient("mongodb://localhost:27017/")        
db = client['Real_Time_Weather']
collection = db["sample"]

os.environ['PYSPARK_SUBMIT_ARGS'] = '--jars file:///C:/Users/Ansuman/Hackathon-QuantumX-master/python_login/mongo-spark-connector_2.12-3.0.1-assembly.jar pyspark-shell'
spark = SparkSession.builder \
    .appName("MyApp") \
    .config("spark.mongodb.output.uri", "mongodb://localhost:27017/") \
    .config("spark.mongodb.output.collection", collection) \
    .getOrCreate()
    

# http://localhost:5000/pythonlogin/ - the following will be our login page, which will use both GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def login():
    return render_template('index1.html')

@app.route('/test', methods=['GET', 'POST'])
def testfn():
    if request.method == 'GET':
        msg = {"Greetings": "Hello from Flask"}
        return jsonify(msg)

@app.route('/get_city_data/<string:cityInput>', methods=['POST'])
def get_city_data(cityInput):
    # cityInput = json.load(cityInput)
    global loc
    loc = cityInput
    loc = loc[1:-1]
    print(loc)
    try:
        if (db.validate_collection(f"{loc}")):  # Try to validate a collection
            print("Collection exists")
            
            data_pdf = retrieve_data_from_mongo(spark)
            data_df = preprocess_data(data_pdf)
            df = process_for_prophet(data_df, "Temp")
            future = get_future_df()
            model, fore = prophet_model_training(df, future)
            print(fore[["ds","yhat_upper", "yhat_lower", "yhat"]])
    
    except pymongo.errors.OperationFailure:  # If the collection doesn't exist
        print("Collecting History Data")
        data_into_mongo(loc, client)
        print("Data is collected")
        data_pdf = retrieve_data_from_mongo(spark)
        data_df = preprocess_data(data_pdf)
        df = process_for_prophet(data_df, "Temp")
        future = get_future_df()
        model, fore = prophet_model_training(df, future)
        print(fore[["ds","yhat_upper", "yhat_lower", "yhat"]])
    
    return('/')

def data_into_mongo(location, client):
    days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    start_date = "2010-01-01"
    db = client['Real_Time_Weather']
    col = db[location]
    
    for year in [2019, 2020, 2021, 2022]:
        j = 1
        for i in days:
            start_date = "{}-{}-01".format(year,j)
            end_date = "{}-{}-{}".format(year,j,i)
            j += 1
            
            url = "https://api.worldweatheronline.com/premium/v1/past-weather.ashx?key=6052652525c04c6b88b74541222512&q={}&format=json&date={}&enddate={}&includelocation=yes&tp=24".format(location, start_date, end_date)
            response = requests.request("GET", url)
            data = response.json()
            for k in data["data"]["weather"]:
                col.insert_one(k)

def retrieve_data_from_mongo(spark):
    df = spark.read.format("com.mongodb.spark.sql.DefaultSource").option("uri", "mongodb://localhost:27017/Real_Time_Weather.{}".format(loc)).load()
    
    df = df.drop("_id")
    
    hourly_data = df.select("date","hourly.tempC","hourly.windspeedKmph", "hourly.precipMM", "hourly.humidity", "hourly.pressure").toPandas()
    
    return hourly_data

def preprocess_data(data_pdf):
    data_pdf["Temp"] = data_pdf["tempC"].apply(pd.Series)
    data_pdf["Rain"] = data_pdf["precipMM"].apply(pd.Series)
    data_pdf["Humidity"] = data_pdf["humidity"].apply(pd.Series)
    data_pdf["WindSpeed"] = data_pdf["windspeedKmph"].apply(pd.Series)
    data_pdf["Pressure"] = data_pdf["pressure"].apply(pd.Series)
    
    data_pdf = data_pdf.drop(['tempC', 'precipMM', "humidity","windspeedKmph", "pressure"], axis=1)
    
    convert_dict = {'Temp': int,
                'Rain': float,
                'Humidity':int,
                'WindSpeed': int,
                'Pressure': int
                }
    data_pdf = data_pdf.astype(convert_dict)
    data_pdf['date'] = pd.DatetimeIndex(data_pdf['date'])
    
    return data_pdf

def process_for_prophet(data_df, var):
    df = data_df[["date",var]]
    df = df.rename(columns={'date': 'ds',
                        var: 'y'})
    return df

def get_future_df():
    today = date.today()
    d1 = int(today.strftime("%d"))
    future = list()
    for i in range(d1, d1+8):
        dat = '2023-01-%02d' % i
        future.append([dat])
    future = pd.DataFrame(future)
    future.columns = ['ds']
    future['ds']= pd.to_datetime(future['ds'])
    return future

def prophet_model_training(df, future):
    prophet_model= Prophet(interval_width=0.90)
    prophet_model.fit(df)
    forecast = prophet_model.predict(future)
    return prophet_model,forecast


if __name__ == '__main__':
    app.run()
    
# python -m flask --app main.py run --debugger --reload