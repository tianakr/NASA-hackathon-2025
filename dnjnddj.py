import earthaccess
from datetime import datetime
import xarray as xr

EARTHDATA_USERNAME = "nasaspaceapps1"
EARTHDATA_PASSWORD = "My_strongPwd#2025"

def get_start_end_of_day(user_input):
    dt = datetime.strptime(user_input, "%Y-%m-%d %H:%M")
    start_of_day = dt.replace(hour=0, minute=0, second=0)
    end_of_day = dt.replace(hour=23, minute=59, second=59)
    return start_of_day, end_of_day

start, end = get_start_end_of_day("2025-10-04 14:30")
print("Start of day:", start)
print("End of day:", end)

# Search datasets
results = earthaccess.search_datasets(
    keyword="OMUVBd_003",
    bounding_box=(-10, 20, 10, 50),
    temporal=("1999-02-01", "2019-03-31")
)

# EarthAccessResults is iterable
print(f"Found {len(results)} datasets")

# Pick first dataset
dataset = results[0]
print("Dataset ID:", dataset.id)
print("Short name:", dataset.short_name)

# List files in dataset
files = earthaccess.list_files(dataset.id)
print(f"Files available: {len(files)}")

# Pick first file to download
file_info = files[0]
local_file = earthaccess.download_file(file_info.id, ".", EARTHDATA_USERNAME, EARTHDATA_PASSWORD)

# Open NetCDF with xarray
ds = xr.open_dataset(local_file)
print(ds)  # Shows all variables

# UV index variable
uv_index = ds['UV_index']  # could also be 'uv_index' depending on file

# Subset by bounding box
uv_region = uv_index.sel(lat=slice(20,50), lon=slice(-10,10))
print("UV Index for the region (first timestep):", uv_region.isel(time=0).values)
