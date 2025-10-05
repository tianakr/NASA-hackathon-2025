import requests
from datetime import datetime

def get_uv_index(lat, lon, date_str):
    """
    Get the daily UV index for a given location and date using NASA POWER API.

    Args:
        lat (float): Latitude
        lon (float): Longitude
        date_str (str): Date in YYYY-MM-DD format

    Returns:
        float or None: UV index value, or None if not available
    """
    # Convert date to API format YYYYMMDD
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
        print("Error: Could not fetch data from NASA POWER API.")
        return None

    data = response.json()
    
    # Extract UV index
    try:
        uv_index = data["properties"]["parameter"]["ALLSKY_UV_INDEX"][date_api]
        return uv_index
    except KeyError:
        print("UV index data not available for this date/location.")
        return None

# -----------------------------
# Example usage
# -----------------------------

# You can iterate over 10 dates if needed
dates = [
    "2025-06-01", "2025-06-02", "2025-06-03", "2025-06-04", "2025-06-05",
    "2025-06-06", "2025-06-07", "2025-06-08", "2025-06-09", "2025-06-10"
]

lat, lon = 25.276987, 55.296249  # Dubai, UAE (works reliably for UV)

for date in dates:
    uv = get_uv_index(lat, lon, date)
    if uv is not None:
        print(f"UV Index on {date} at ({lat}, {lon}): {uv}")