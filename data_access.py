import requests as req
import json
from datetime import datetime, timedelta


user_lat = float(input("Enter latitude: "))
user_lon = float(input("Enter longitude: "))
user_date = input("Enter date (YYYY-MM-DD): ")
user_time = input("Enter time (HH:MM, 24-hour format): ")
user_hour = int(user_time.split(":")[0])
end_date = datetime.strptime(user_date, "%Y-%m-%d")
start_date = end_date - timedelta(days=90)

def get_uv_data(lat, lon, start_date, end_date, hour, parameter):
    start_date = datetime.strftime(start_date, "%Y%m%d")
    end_date = datetime.strftime(end_date, "%Y%m%d")
    
    API_URL = f"https://power.larc.nasa.gov/api/temporal/hourly/point?start={start_date}&end={end_date}&latitude=10&longitude=10&community=re&parameters={parameter}&format=json&units=metric&header=true"

    response = req.get(API_URL)
    data = response.json()
    with open(f"{parameter}.json", "w+") as data_file:
        json.dump(data, data_file, indent=4)
    """uv_data = data["properties"]["parameter"]["ALLSKY_SFC_UV_INDEX"]

    uv_values = []
    for key, value in uv_data.items():
        # Example key: "20250901:14Z"
        if key.endswith(f"{hour:02d}Z"):  # keep only data for that hour
            uv_values.append(value)

    return uv_values"""


uv_values = get_uv_data(user_lat, user_lon, start_date, end_date, user_hour, "ALLSKY_SFC_UV_INDEX")

print(uv_values)
"""def fetch_data(lat, lon, start_date, end_date, parameter):
    API_URL = f"https://power.larc.nasa.gov/api/temporal/daily/point?start={start_date}&end={end_date}&latitude={lat}&longitude={lon}&community=RE&parameters={parameter}&time-standard=LST&format=JSON"
    response = req.get(API_URL)
    data = response.json()
    with open(f"{parameter}.json", "w+") as data_file:
        json.dump(data, data_file, indent=4)

fetch_data("40", "-100", "20250601", "20250602", "ALLSKY_SFC_UV_INDEX")"""