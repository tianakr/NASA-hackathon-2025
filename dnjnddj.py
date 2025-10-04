import earthaccess
from datetime import datetime
import xarray as xr

# NASA Earthdata login
EARTHDATA_USERNAME = "nasaspaceapps1"
EARTHDATA_PASSWORD = "My_strongPwd#2025"

def get_start_end_of_day(user_input):
    """
    Takes a datetime string and returns the start and end of that day.

    Args:
        user_input (str): Date/time in format "YYYY-MM-DD HH:MM"

    Returns:
        tuple: (start_of_day, end_of_day)
    """
    dt = datetime.strptime(user_input, "%Y-%m-%d %H:%M")
    start_of_day = dt.replace(hour=0, minute=0, second=0)
    end_of_day = dt.replace(hour=23, minute=59, second=59)
    return start_of_day, end_of_day

# Example date
start, end = get_start_end_of_day("2025-10-04 14:30")
print("Start of day:", start)
print("End of day:", end)

# Corrected search_datasets call
results = earthaccess.search_datasets(
    keyword="OMUVBd_003",
    bounding_box=(-10, 20, 10, 50),
    temporal=("1999-02-01", "2019-03-31")
)

# Check datasets found
print(f"Found {len(results['hits'])} datasets")

# Pick the first dataset
dataset_id = results['hits'][0]['id']

# List files in this dataset
files = earthaccess.list_files(dataset_id)
print(f"Files available: {len(files['items'])}")

# Download the first file
file_info = files['items'][0]
local_file = earthaccess.download_file(file_info['id'], ".", EARTHDATA_USERNAME, EARTHDATA_PASSWORD)

# Open with xarray
ds = xr.open_dataset(local_file)
print(ds)  # shows all variables

# Extract UV index variable (usually named 'UV_index')
uv_index = ds['UV_index']

# Subset by bounding box
uv_region = uv_index.sel(lat=slice(20,50), lon=slice(-10,10))

# Example: print UV index for the first time in the file
print("UV Index values for the region:", uv_region.isel(time=0).values)