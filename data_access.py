import requests as req
import json
from datetime import datetime, timedelta
from matplotlib import pyplot as plt

user_lat = float(input("Enter latitude: "))
user_lon = float(input("Enter longitude: "))
user_date = input("Enter date (YYYY-MM-DD): ")
end_date = datetime.strptime(user_date, "%Y-%m-%d")
start_date = end_date - timedelta(days=90)

def get_data(lat, lon, start_date, end_date, parameter):
    start_date = datetime.strftime(start_date, "%Y%m%d")
    end_date = datetime.strftime(end_date, "%Y%m%d")
    list_values = []

    API_URL = f"https://power.larc.nasa.gov/api/temporal/daily/point?start={start_date}&end={end_date}&latitude=10&longitude=10&community=re&parameters={parameter}&format=json&units=metric&header=true"

    response = req.get(API_URL)
    data_frame = response.json()
    data = data_frame["properties"]["parameter"][parameter]
    
    for value in data.values():
        list_values.append(value)
    return list_values

uv_values = get_data(user_lat, user_lon, start_date, end_date, "ALLSKY_SFC_UV_INDEX")

plt.plot(uv_values)
plt.show()