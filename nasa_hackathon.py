from geopy.geocoders import Nominatim
import requests as req
import json
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import pandas as pd
from prophet import Prophet
import numpy as np
from scipy.stats import gamma, norm


def main_location():
    loc = Nominatim(user_agent="Geopy Library")

    getLoc = loc.geocode(input("Enter your address: "))
    latitude = getLoc.latitude
    longitude = getLoc.longitude

    return latitude, longitude

def main_date():
    date = input("Enter the date (YYYY-MM-DD): ")
    if len(date) == 10 and date[4] == '-' and date[7] == '-':
        print(f"Date set to: {date}")
    else:
        print("Warning: Date should be in YYYY-MM-DD format!")
    return date

def get_data_daily(lat, lon, start_date, end_date, quantity):
    start_date = datetime.strftime(start_date, "%Y%m%d")
    end_date = datetime.strftime(end_date, "%Y%m%d")
    list_values = []

    API_URL = f"https://power.larc.nasa.gov/api/temporal/daily/point?start={start_date}&end={end_date}&latitude={lat}&longitude={lon}&community=re&parameters={quantity}&format=json&units=metric&header=true"

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

    API_URL = f"https://power.larc.nasa.gov/api/temporal/hourly/point?start={start_date}&end={end_date}&latitude={lat}&longitude={lon}&community=re&parameters={quantity}&format=json&units=metric&header=true"

    response = req.get(API_URL)
    data = response.json()
    dict_data = data["properties"]["parameter"][quantity]
    
    for key, value in dict_data.items():
        if key.endswith(f"{hour:02d}"):
            list_values.append(value)
    return list_values

def forecast_quantity(start_date, end_date, target_date, values_list):
    print(values_list)

    dates = pd.date_range(start=start_date, end=end_date)
    df = pd.DataFrame({
        "ds": dates,
        "y": values_list
    })

    df = df[df["y"] != -999] #remove any values = -999
    
    model = Prophet()
    model.fit(df)

    future = pd.date_range(start=df["ds"].max() + pd.Timedelta(days=1),
                       end=target_date,
                       freq="D")
    future_df = pd.DataFrame({"ds": future})

    # Predict the UV for the next day (or any specific date)

    forecast = model.predict(future_df)
    predicted_value = forecast.loc[forecast["ds"] == target_date, "yhat"].values[0]
    print(f"\nPredicted UV index for {target_date.date()}: {predicted_value:.2f}")

    model.plot(forecast)
    plt.title("UV Index Forecast with NASA Data")
    plt.xlabel("Date")
    plt.ylabel("UV Index")
    plt.show()

    forecast_dict = {"mean" : forecast["yhat"], "lower" : forecast["yhat_lower"], "upper" : forecast["yhat_upper"]}
    return forecast_dict

def find_probability_range(dict_norm_dist, lower, upper):
    upper_limit = float(upper)
    lower_limit = float(lower)
    mu = float(dict_norm_dist["mean"].iloc[0])
    sigma = float(((dict_norm_dist["upper"] - dict_norm_dist["lower"]) / 3.92).iloc[0])
    
    probability = (norm.cdf(upper_limit, mu, sigma) - norm.cdf(lower_limit, mu, sigma)) * 100
    print(f"probability is: {probability:.2f}%")
    
    return probability

def precipitation_probability(coordinates, date):
    user_msg = """Pick an option:
        1. No Rain
        2. Light Rain
        3. Moderate Rain
        4. Heavy Rain
        5. Extreme Rain"""
    lat = coordinates[0]
    lon = coordinates[1]
    target_date = datetime.strptime(date, "%Y-%m-%d")
    end_date = target_date - timedelta(days=1)
    start_date = end_date - timedelta(days=900)
    lower = None
    upper = None
    
    print(user_msg)

    user_choice = int(input("Type a number between 1-5: "))

    match user_choice:
        case 1:
            lower = 0
            upper = 0.1
        case 2:
            lower = 0.1
            upper = 2.5
        case 3:
            lower = 2.6
            upper = 7.5
        case 4:
            lower = 7.6
            upper = 50
        case 5:
            lower = 100
            upper = 500
        case _:
                print("Choice Invalid!")
    
    precipitation_values = get_data_daily(lat, lon, start_date, end_date, "PRECTOTCORR")
    precipitation_forecast_dict = forecast_quantity(start_date, end_date, target_date, precipitation_values)
    find_probability_range(precipitation_forecast_dict, lower, upper)

def uv_probability(coordinates, date):
    user_msg = """Pick an option to check probability:
        1. Low
        2. Moderate
        3. High
        4. Very High
        5. Extreme"""
    lat = coordinates[0]
    lon = coordinates[1]
    target_date = datetime.strptime(date, "%Y-%m-%d")
    target_time = input("Enter time (HH:MM): ")
    end_date = target_date - timedelta(days=1)
    start_date = end_date - timedelta(days=900)
    lower = None
    upper = None
    

    print(user_msg)
    
    user_choice = int(input("Type a number between 1-5: "))

    match user_choice:
        case 1:
            lower = 0
            upper = 2
        case 2:
            lower = 2
            upper = 5
        case 3:
            lower = 5
            upper = 7
        case 4:
            lower = 7
            upper = 10
        case 5:
            lower = 10
            upper = 50
        case _:
                print("Choice Invalid!")

    uv_values = get_data_hourly(lat, lon, start_date, end_date, target_time, "ALLSKY_SFC_UV_INDEX")
    uv_forecast_dict = forecast_quantity(start_date, end_date, target_date, uv_values)
    find_probability_range(uv_forecast_dict, lower, upper)

def wind_probability(coordinates, date):
    user_msg = """Pick an option to check probability:
        1. Calm
        2. Moderate
        3. Strong
        4. Very Strong
        5. Violent"""
    lat = coordinates[0]
    lon = coordinates[1]
    target_date = datetime.strptime(date, "%Y-%m-%d")
    target_time = input("Enter time (HH:MM): ")
    end_date = target_date - timedelta(days=1)
    start_date = end_date - timedelta(days=900)
    lower = None
    upper = None
    
    print(user_msg)
    
    user_choice = int(input("Type a number between 1-5: "))

    match user_choice:
        case 1:
            lower = 0
            upper = 3
        case 2:
            lower = 3
            upper = 8
        case 3:
            lower = 8
            upper = 14
        case 4:
            lower = 14
            upper = 20
        case 5:
            lower = 20
            upper = 200
        case _:
                print("Choice Invalid!")

    uv_values = get_data_hourly(lat, lon, start_date, end_date, target_time, "ALLSKY_SFC_UV_INDEX")
    uv_forecast_dict = forecast_quantity(start_date, end_date, target_date, uv_values)
    find_probability_range(uv_forecast_dict, lower, upper)

def temp_probability(coordinates, date):
    user_msg = """Pick an option to check probability:
        1. Extreme Cold
        2. Cold
        3. Mild
        4. Warm
        5. Hot
        6. Extreme Heat"""
    lat = coordinates[0]
    lon = coordinates[1]
    target_date = datetime.strptime(date, "%Y-%m-%d")
    target_time = input("Enter time (HH:MM): ")
    end_date = target_date - timedelta(days=1)
    start_date = end_date - timedelta(days=900)
    lower = None
    upper = None
    
    print(user_msg)
    
    user_choice = int(input("Type a number between 1-5: "))

    match user_choice:
        case 1:
            lower = -200
            upper = -20
        case 2:
            lower = -20
            upper = 10
        case 3:
            lower = 10
            upper = 20
        case 4:
            lower = 20
            upper = 30
        case 5:
            lower = 30
            upper = 35
        case 6:
            lower = 35
            upper = 100
        case _:
                print("Choice Invalid!")

    temp_values = get_data_hourly(lat, lon, start_date, end_date, target_time, "T2M")
    temp_forecast_dict = forecast_quantity(start_date, end_date, target_date, temp_values)
    find_probability_range(temp_forecast_dict, lower, upper)

def main():
    menu_text = """Will it rain on my parade!
    1. Coordinates
    2. Temperature Probability
    3. Precipitation Probability
    4. UV Index
    5. Wind Speed
    6. Exit"""
    coordinates = main_location()
    date = main_date()
    user_choice = None

    while user_choice != 6:
        print(menu_text)
        user_choice = int(input("Type your choice 1-6!: "))

        match user_choice:
            case 1:
                print(coordinates[0], coordinates[1])
            case 2:
                temp_probability
            case 3:
                precipitation_probability(coordinates, date)
            case 4:
                uv_probability(coordinates, date)
            case 5:
                wind_probability(coordinates, date)
            case 6:
                print("Thank you for playing the game!")
            case _:
                "Choice invalid. Pick a number between 1-6!"

if __name__ == "__main__":
    main()