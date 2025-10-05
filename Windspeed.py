import requests as req
import json
from datetime import datetime, timedelta

user_lat = float(input("Enter latitude: "))
user_lon = float(input("Enter longitude: "))
user_date = input("Enter date (YYYY-MM-DD): ")
#user_time = input("Enter time (HH:MM, 24-hour format): ")

end_date = datetime.strptime(user_date, "%Y-%m-%d")
start_date = end_date - timedelta(days=90)

start_str = datetime.strftime(start_date, "%Y%m%d")
end_str = datetime.strftime(end_date, "%Y%m%d")

def get_windspeed(user_lat,user_lon,start_str,end_str,parameter):
    Entire_list = []
    API_URL = f"https://power.larc.nasa.gov/api/temporal/daily/point?start={start_str}&end={end_str}&latitude=10&longitude=10&community=re&parameters={parameter}&format=json&units=metric&header=true"

    response = req.get(API_URL)
    data = response.json()

    wind_speed = data["properties"]["parameter"][parameter]

    for wind_speed_per_day in wind_speed.values() :
        Entire_list.append(wind_speed_per_day)

    return Entire_list 

a = get_windspeed(user_lat,user_lon,start_str,end_str,"WS2M")
print(a)

