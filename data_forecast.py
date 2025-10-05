import requests as req
import json
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import pandas as pd
from prophet import Prophet
import numpy as np


def get_data_daily(lat, lon, start_date, end_date, quantity):
    start_date = datetime.strftime(start_date, "%Y%m%d")
    end_date = datetime.strftime(end_date, "%Y%m%d")
    list_values = []

    API_URL = f"https://power.larc.nasa.gov/api/temporal/daily/point?start={start_date}&end={end_date}&latitude=10&longitude=10&community=re&parameters={quantity}&format=json&units=metric&header=true"

    response = req.get(API_URL)
    data = response.json()
    dict_data = data["properties"]["parameter"][quantity]
    
    for value in dict_data.values():
        list_values.append(value)
    return list_values


def get_data_hourly(lat, lon, start_date, end_date, time, quantity):
    start_date = datetime.strftime(start_date, "%Y%m%d")
    end_date = datetime.strftime(end_date, "%Y%m%d")
    hour = int(time.split(":")[0])
    list_values = []

    API_URL = f"https://power.larc.nasa.gov/api/temporal/hourly/point?start={start_date}&end={end_date}&latitude=10&longitude=10&community=re&parameters={quantity}&format=json&units=metric&header=true"

    response = req.get(API_URL)
    data = response.json()
    dict_data = data["properties"]["parameter"][quantity]
    
    for key, value in dict_data.items():
        if key.endswith(f"{hour:02d}"):
            list_values.append(value)
    return list_values


def forecast_quantity(start_date, end_date, target_date, values_list):
    dates = pd.date_range(start=start_date, end=end_date)
    df = pd.DataFrame({
        "ds": dates,
        "y": values_list
    })
    model = Prophet()
    model.fit(df)

    # Predict the UV for the next day (or any specific date)
    future = pd.DataFrame({
        "ds": [target_date]  # next day
    })

    forecast = model.predict(future)
    predicted_value = forecast["yhat"].values[0]

    print(f"Predicted UV index for {future['ds'].iloc[0].date()}: {predicted_value:.2f}")


user_lat = float(input("Enter latitude: "))
user_lon = float(input("Enter longitude: "))
target_date = datetime.strptime(input("Enter date (YYYY-MM-DD): "), "%Y-%m-%d")
target_time = input("Enter time (HH:MM): ")
end_date = target_date - timedelta(days=1)
start_date = end_date - timedelta(days=90)

uv_values = get_data_hourly(user_lat, user_lon, start_date, end_date, target_time, "ALLSKY_SFC_UV_INDEX")

forecast_quantity(start_date, end_date, target_date, uv_values)

#plt.plot(uv_values)

#plt.show()