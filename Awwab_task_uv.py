import requests
from datetime import datetime

def get_uv_index(lat, lon, date_str):
    """
    Get UV index for a location (lat, lon) and date (YYYY-MM-DD).
    """
    # Convert date to API format
    date_api = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y%m%d")

    # NASA POWER API URL
    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"parameters=ALLSKY_UV_INDEX&community=RE"
        f"&latitude={lat}&longitude={lon}"
        f"&start={date_api}&end={date_api}&format=JSON"
    )

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching data: HTTP {response.status_code}")
        return None

    data = response.json()

    try:
        uv_index = data["properties"]["parameter"]["ALLSKY_UV_INDEX"][date_api]
        return uv_index
    except KeyError:
        print("UV index data not available for this date/location.")
        return None

# Example usage:
lat, lon = 59.33, 18.06  # Stockholm, Sweden
date = "2023-06-21"       # Past date
uv = get_uv_index(lat, lon, date)

if uv is not None:
    print(f"UV Index on {date} at ({lat}, {lon}): {uv}")