import requests as req
import json
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import pandas as pd
from prophet import Prophet
import numpy as np
from scipy.stats import norm


user_lat = float(input("Enter latitude: "))
user_lon = float(input("Enter longitude: "))
user_date = input("Enter date (YYYY-MM-DD): ")
user_time = input("Enter time (HH:MM, 24-hour format): ")

end_date = datetime.strptime(user_date, "%Y-%m-%d")       
start_date = end_date - timedelta(days=90)

start_str = datetime.strftime(start_date, "%Y%m%d")
end_str = datetime.strftime(end_date, "%Y%m%d")

target_date = end_date + timedelta(days=1)

hour = int(user_time.split(":")[0]) #Useful for line 30


def get_data_hourly(lat, lon, start_date, end_date, time, quantity):
    start_str = datetime.strftime(start_date, "%Y%m%d")               #
    end_str = datetime.strftime(end_date, "%Y%m%d")
    list_values = []
    list_dates = []

    API_URL = f"https://power.larc.nasa.gov/api/temporal/hourly/point?start={start_str}&end={end_str}&latitude=10&longitude=10&community=re&parameters={quantity}&format=json&units=metric&header=true"

    response = req.get(API_URL)
    data = response.json()
    dict_data = data["properties"]["parameter"][quantity]
    
    for key, value in dict_data.items():
        if key.endswith(f"{hour:02d}"):
            list_values.append(value)
            list_dates.append(key[0:8]) #To ge YYYYMMDD for the date

#Check google doc for dic_data, but key value pair is     "2023050100": 3.2

    return list_values,list_dates

#dates,values= get_data_hourly(user_lat,user_lon,start_date,end_date,hour,"WS2M")
values, dates = get_data_hourly(user_lat, user_lon, start_date, end_date, hour, "WS2M")

#print(f"Dates : {dates}")
#print(f"Values : {values}")

plt.figure(figsize=(12,6))
plt.plot(dates, values, marker='o')
plt.xticks(rotation=45)
plt.xlabel("Date")
plt.ylabel(f"Wind Speed at {hour:02d}:00 (m/s)")
plt.title(f"Wind Speed at Hour {hour:02d}:00 Over 90 Days")
plt.grid(True)
plt.tight_layout()
plt.show()

# This prints two different lists one for dates, one for values

def forecast_quantity(start_date, end_date, target_date, values_list):
    dates = pd.date_range(start=start_date, end=end_date)
    print(values_list)
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

    print(f"Predicted wind speed for {future['ds'].iloc[0].date()}: {predicted_value:.2f}")

    forecast_dict = {"mean" : forecast["yhat"], "lower" : forecast["yhat_lower"], "upper" : forecast["yhat_upper"]}
    return forecast_dict


def find_probability_range(dict_norm_dist):
    upper_limit = float(input("Enter the upper limit for the norm cdf: "))
    lower_limit = float(input("Enter the lower limit for the norm cdf: "))
    mu = float(dict_norm_dist["mean"].iloc[0])
    
    sigma = float(((dict_norm_dist["upper"] - dict_norm_dist["lower"]) / 3.92).iloc[0])
    #print(mu)
    #print(sigma)
    probability = (norm.cdf(upper_limit, mu, sigma) - norm.cdf(lower_limit, mu, sigma)) * 100
    #print("probability is: ", probability)
    return probability

forecast_result = forecast_quantity(start_date, end_date, target_date, values)
#find_probability_range(forecast_result)
rounded_proability = find_probability_range(forecast_result)
print(f"Probability for target wind speed is {rounded_proability:.2f}")

 
