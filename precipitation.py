import requests as req
import json
from datetime import datetime, timedelta


user_lat = float(input("Enter latitude: "))
user_lon = float(input("Enter longitude: "))
user_date = input("Enter date (YYYY-MM-DD): ")

end_date = datetime.strptime(user_date, "%Y-%m-%d")
start_date = end_date - timedelta(days=90)

def get_precipitation_data(lat, lon, start_date, end_date, parameter = "PRECTOT"):
    start_date = datetime.strftime(start_date, "%Y%m%d")
    end_date = datetime.strftime(end_date, "%Y%m%d")
    
    API_URL = f"https://power.larc.nasa.gov/api/temporal/daily/point?start={start_date}&end={end_date}&latitude=10&longitude=10&community=re&parameters={parameter}&format=json&units=metric&header=true"

    response = req.get(API_URL)
    data = response.json()
    with open(f"{parameter}.json", "w+") as data_file:
        json.dump(data, data_file, indent=4)
    """precipitation = data["properties"]["parameter"]["IMERG_PRECTOT"]

    precipitation = []
    for key, value in precipitation.data.items():
        # Example key: "20250901:14Z"
        if key.endswith(f"{day:02d}Z"):  # keep only data for that day
            uv_values.append(value)

    return precipitation"""


precipitation = get_precipitation_data(user_lat, user_lon, start_date, end_date,"IMERG_PRECTOT")

print(get_precipitation_data) #prints mm per day 90 days

#add all elements from the list

#divide by 90

#average precipitation during 3 months

#

"""def fetch_data(lat, lon, start_date, end_date, parameter):
    API_URL = f"https://power.larc.nasa.gov/api/temporal/daily/point?start={start_date}&end={end_date}&latitude={lat}&longitude={lon}&community=RE&parameters={parameter}&time-standard=LST&format=JSON"
    response = req.get(API_URL)
    data = response.json()
    with open(f"{parameter}.json", "w+") as data_file:
        json.dump(data, data_file, indent=4)

fetch_data("40", "-100", "20250601", "20250602", "IMERG_PRECTOT")"""

#condition of interest (heat, cold, wind, wetness, or comfort).pip show earthaccess

#def precipitation_probability(date, location):
 #   pop = confidence * areal_coverage_mm
    #That’s the probability that any random point in the area gets measurable precipitation.
  #  probability_precipitation = (num_wet/total_periods) * 100 
   # return probability_precipitation