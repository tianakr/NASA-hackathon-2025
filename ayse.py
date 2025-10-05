
from geopy.geocoders import Nominatim
import requests
from datetime import datetime, date, timezone


WINDOW_DAYS  = 14    
THRESHOLD_MM = 1.0    
SNOW_TEMP_C  = 0.0    

def location():
    
    geo = Nominatim(user_agent="will-it-rain/1.0")
    loc = geo.geocode(input("City/address: ").strip())
    if not loc:
        raise SystemExit("Address not found.")
    return float(loc.latitude), float(loc.longitude)

def precip_probs_climo(lat: float, lon: float, date_str: str,
                       window_days: int = WINDOW_DAYS,
                       thr_mm: float = THRESHOLD_MM):
    
    start = "19840101"
    end   = datetime.now(timezone.utc).strftime("%Y%m%d")
    api = (
        "https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?start={start}&end={end}"
        f"&latitude={lat}&longitude={lon}"
        f"&community=RE&parameters=PRECTOTCORR,T2M&format=JSON"
    )
    r = requests.get(api); r.raise_for_status()
    param = r.json()["properties"]["parameter"]
    precip = param["PRECTOTCORR"] 
    temp   = param["T2M"]          

    
    tgt = datetime.strptime(date_str, "%Y-%m-%d").date()

    def doy(d: date):
        if d.month == 2 and d.day == 29:
            return 59
        return d.timetuple().tm_yday

    center = doy(tgt)

    def in_window(dn: int, c: int, w: int) -> bool:
        low, high = c - w, c + w
        if low < 1:
            return dn <= high or dn >= 365 + low
        if high > 365:
            return dn >= low or dn <= (high - 365)
        return low <= dn <= high

    
    total = rain = snow = 0
    for k, v in precip.items():
        d = datetime.strptime(k, "%Y%m%d").date()
        if not in_window(doy(d), center, window_days):
            continue
        try:
            mm = float(v)
            tc = float(temp[k])
        except Exception:
            continue
        total += 1
        if mm >= thr_mm:
            if tc > SNOW_TEMP_C:
                rain += 1
            else:
                snow += 1

    if total == 0:
        return {"rain": 0.0, "snow": 0.0}

    pct = lambda x: round(100.0 * x / total, 1)
    return {"rain": pct(rain), "snow": pct(snow)}


if __name__ == "__main__":
    lat, lon  = location()                              
    date_str  = input("Enter date (YYYY-MM-DD): ").strip()
    probs     = precip_probs_climo(lat, lon, date_str)


    print(f"Rain: {probs['rain']}%")
    print(f"Snow: {probs['snow']}%")