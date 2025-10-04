import earthaccess
from datetime import datetime
import h5py
import numpy as np

# -----------------------------
# 1️⃣ NASA Earthdata credentials
# -----------------------------
EARTHDATA_USERNAME = "nasaspaceapps1"
EARTHDATA_PASSWORD = "My_strongPwd#2025"

# -----------------------------
# 2️⃣ Function to get start and end of day
# -----------------------------
def get_start_end_of_day(user_input):
    dt = datetime.strptime(user_input, "%Y-%m-%d %H:%M")
    start_of_day = dt.replace(hour=0, minute=0, second=0)
    end_of_day = dt.replace(hour=23, minute=59, second=59)
    return start_of_day, end_of_day

# -----------------------------
# 3️⃣ Example date input
# -----------------------------
user_input = "2025-10-04 14:30"
start, end = get_start_end_of_day(user_input)

print("Start of day:", start)
print("End of day:", end)

# -----------------------------
# 4️⃣ Log in to NASA Earthdata
# -----------------------------
auth = earthaccess.login(username=EARTHDATA_USERNAME, password=EARTHDATA_PASSWORD)

# -----------------------------
# 5️⃣ Search for the UV dataset granules
# -----------------------------
results = earthaccess.search_data(
    short_name="OMUVBd_003",                          # UV dataset
    bounding_box=(10, 55, 20, 70),                   # Sweden region example
    temporal=(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")),  # Use start/end
    count=1                                           # Just 1 file
)

print(f"Number of granules found: {len(results)}")

# -----------------------------
# 6️⃣ Download the UV file
# -----------------------------
earthaccess.download(results, "./uv_data")
print("Download complete!")

# -----------------------------
# 7️⃣ Read UV index value from the file
# -----------------------------
# Get the downloaded file name
file_name = results[0]["download_url"].split("/")[-1]
file_path = "./uv_data/" + file_name

# Example location (Stockholm)
lat, lon = 59.33, 18.06

with h5py.File(file_path, "r") as f:
    uv_data = f['EGEN_UV_INDEX'][:]
    lat_data = f['Latitude'][:]
    lon_data = f['Longitude'][:]

    # Find nearest grid point
    lat_idx = (np.abs(lat_data - lat)).argmin()
    lon_idx = (np.abs(lon_data - lon)).argmin()

    uv_index = uv_data[lat_idx, lon_idx]

print(f"UV Index on {user_input} at ({lat}, {lon}): {uv_index}")