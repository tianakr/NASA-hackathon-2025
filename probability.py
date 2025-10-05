import requests as req
import json
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import pandas as pd
from prophet import Prophet
import numpy as np
from scipy.stats import norm


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

    forecast_dict = {"mean" : forecast["yhat"], "lower" : forecast["yhat_lower"], "upper" : forecast["yhat_upper"]}
    return forecast_dict


def find_probability_range(dict_norm_dist):
    upper_limit = float(input("Enter the upper limit for the norm cdf: "))
    lower_limit = float(input("Enter the lower limit for the norm cdf: "))
    mu = float(dict_norm_dist["mean"].iloc[0])
    sigma = float(((dict_norm_dist["upper"] - dict_norm_dist["lower"]) / 3.92).iloc[0])
    
    probability = (norm.cdf(upper_limit, mu, sigma) - norm.cdf(lower_limit, mu, sigma)) * 100
    print("probability is: ", probability)
    
    return probability


user_lat = float(input("Enter latitude: "))
user_lon = float(input("Enter longitude: "))
target_date = datetime.strptime(input("Enter date (YYYY-MM-DD): "), "%Y-%m-%d")
target_time = input("Enter time (HH:MM): ")
end_date = target_date - timedelta(days=1)
start_date = end_date - timedelta(days=900)

uv_values = get_data_hourly(user_lat, user_lon, start_date, end_date, target_time, "ALLSKY_SFC_UV_INDEX")

uv_forecast_dict = forecast_quantity(start_date, end_date, target_date, uv_values)
find_probability_range(uv_forecast_dict)

#plt.plot(uv_values)

#plt.show()