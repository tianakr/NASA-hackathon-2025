import time
import os
import requests
from datetime import datetime, date as dt_date, timedelta

# -----------------------------
# MENÜ VE GİRİŞ FONKSİYONLARI
# -----------------------------
def menu():
    return ("""Welcome to will it rain on my parade!
            1. Location
            2. Date
            3. Extreme temp
            4. Precipitation probability
            5. UV index
            6. Wind
            7. Exit
            """)

def location():
    lat = float(input("Enter latitude (e.g., 34.05): "))
    lon = float(input("Enter longitude (e.g., -118.25): "))
    if -90 <= lat <= 90 and -180 <= lon <= 180:
        print(f"Location set to: Latitude {lat}, Longitude {lon}")
    else:
        print("Warning: Latitude must be -90 to 90 and Longitude must be -180 to 180!")
    return (lat, lon)

def date():
    d = input("Enter the date (YYYY-MM-DD): ")
    if len(d) == 10 and d[4] == '-' and d[7] == '-':
        print(f"Date set to: {d}")
    else:
        print("Warning: Date should be in YYYY-MM-DD format!")
    return d

# -----------------------------
# NASA POWER: VERİ YARDIMCILARI
# -----------------------------
POWER_BASE = "https://power.larc.nasa.gov/api/temporal/daily/point"
POWER_VARS = ["T2M","T2M_MAX","T2M_MIN","RH2M","WS10M","PRECTOTCORR"]

def _fetch_power_daily(lat, lon, start_date: dt_date, end_date: dt_date):
    """
    Lat/Lon için start–end arası günlük POWER verisini çeker.
    Dönen yapı: [(date, {T2M, T2M_MAX, ...}), ...]
    Birimler: T(°C), RH(%), WS(m/s), PRECTOTCORR(mm/gün)
    """
    params = {
        "parameters": ",".join(POWER_VARS),
        "community": "RE",
        "latitude": f"{lat}",
        "longitude": f"{lon}",
        "start": start_date.strftime("%Y%m%d"),
        "end": end_date.strftime("%Y%m%d"),
        "format": "JSON"
    }
    r = requests.get(POWER_BASE, params=params, timeout=60)
    r.raise_for_status()
    js = r.json()
    param = js.get("properties", {}).get("parameter", {})

    rows = {}
    for var in POWER_VARS:
        for k, v in param.get(var, {}).items():
            try:
                rows.setdefault(k, {})[var] = float(v)
            except (TypeError, ValueError):
                pass

    parsed = []
    for k, d in rows.items():
        try:
            dt = datetime.strptime(k, "%Y%m%d").date()
            parsed.append((dt, d))
        except ValueError:
            continue
    parsed.sort(key=lambda x: x[0])
    return parsed

def _day_of_year_window(center: dt_date, window_days: int, d: dt_date):
    """
    DOY (day-of-year) etrafında dairesel mevsim penceresi kontrolü.
    29 Şubat -> 28 Şubat'a eşlenir.
    """
    def doy(x: dt_date):
        y = x
        if x.month == 2 and x.day == 29:
            y = dt_date(x.year, 2, 28)
        return y.timetuple().tm_yday

    c = doy(center)
    dd = doy(d)
    dist = min((dd - c) % 365, (c - dd) % 365)
    return dist <= window_days

def _sample_window(lat, lon, target_date_str: str, window_days: int = 14, first_year: int = 1984):
    """
    Seçilen tarih (YYYY-MM-DD) etrafında ±window_days mevsimsel pencere için
    tüm yıllardan örneklem döndürür.
    """
    tgt = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    start = dt_date(first_year, 1, 1)
    end   = dt_date.today()
    data = _fetch_power_daily(lat, lon, start, end)
    sample = [(dt, vals) for dt, vals in data if _day_of_year_window(tgt, window_days, dt)]
    return sample  # [(date, {T2M, T2M_MAX, ...}), ...]

# -----------------------------
# ANALİZ FONKSİYONLARI
# -----------------------------
#<<<<<<< HEAD
def extreme_temp(date, location):
    # Orijinal HEAD yer tutucusunu bozmamak için pass değil, aşağıdaki gerçek fonksiyona yönlendirelim.
    return _extreme_temp_impl(date, location)
#=======

def _extreme_temp_impl(date_str, location, window_days=14, hot_thr=35.0, cold_thr=-5.0):
    """
    Seçilen tarih için mevsimsel pencerede:
    - 'very hot' olasılığı: T2M_MAX > hot_thr
    - 'very cold' olasılığı: T2M_MIN < cold_thr
    Ortalama T2M bilgi amaçlı raporlanır.
    """
    lat, lon = location
    sample = _sample_window(lat, lon, date_str, window_days=window_days)
    if not sample:
        return "Veri bulunamadı ya da örneklem boş."

    n = len(sample)
    very_hot = sum(1 for _, v in sample if v.get("T2M_MAX", -1e9) > hot_thr)
    very_cold = sum(1 for _, v in sample if v.get("T2M_MIN", 1e9) < cold_thr)

    p_hot = round(100.0 * very_hot / n, 1)
    p_cold = round(100.0 * very_cold / n, 1)

    avg_t = round(sum(v.get("T2M", 0.0) for _, v in sample) / n, 1)

    if p_hot >= 50:
        return f"Its very hot! ☀️ The average temp at {location} is {avg_t}°C. (Very hot odds: {p_hot}%)"
    elif p_cold >= 50:
        return f"Its very cold! 🥶 The average temp at {location} is {avg_t}°C. (Very cold odds: {p_cold}%)"
    else:
        return (f"The conditions at {location} are mostly normal around this day-of-year. "
                f"Very hot odds: {p_hot}%, Very cold odds: {p_cold}%, Avg T2M ≈ {avg_t}°C.")
#>>>>>>> b506a3cac7370cc8f86d18e6904606d217346444

def precipitation_probability(date, location, window_days=14, wet_thr_mm=20.0):
    """
    PRECTOTCORR (mm/gün) >= wet_thr_mm olan günlerin oranı (mevsimsel pencere).
    Dönüş: yüzde (%).
    """
    lat, lon = location
    sample = _sample_window(lat, lon, date, window_days=window_days)
    if not sample:
        return 0.0
    n = len(sample)
    wet_days = sum(1 for _, v in sample if v.get("PRECTOTCORR", 0.0) >= wet_thr_mm)
    return round(100.0 * wet_days / n, 1)

def uv_index():
    # POWER günlük clear-sky UV sağlamıyor; ileride OMI/OMUVB veya başka bir kaynakla eklenebilir.
    print("UV index is not implemented yet (data source pending).")
    return None

def calculate_wind():
    wind_speed_ms = float(input("Enter wind speed in meters per second(m/s): "))
    wind_speed_mph = wind_speed_ms * 2.2369

    if wind_speed_mph < 1:
        beaufort_number = 0; description  = "Calm"
    elif wind_speed_mph <= 3:
        beaufort_number = 1; description = "Light Air"
    elif wind_speed_mph <= 7:
        beaufort_number = 2; description = "Light Breeze"
    elif wind_speed_mph <= 12:
        beaufort_number = 3; description = "Gentle Breeze"
    elif wind_speed_mph <= 18:
        beaufort_number = 4; description = "Moderate Breeze"
    elif wind_speed_mph <= 24:
        beaufort_number = 5; description = "Fresh Breeze"
    elif wind_speed_mph <= 31:
        beaufort_number = 6; description = "Strong Breeze"
    elif wind_speed_mph <= 38:
        beaufort_number = 7; description = "Near Gale"
    elif wind_speed_mph <= 46:
        beaufort_number = 8; description = "Gale"
    elif wind_speed_mph <= 54:
        beaufort_number = 9; description = "Strong Gale "
    elif wind_speed_mph <= 63:
        beaufort_number = 10; description = "Whole Gale"
    elif wind_speed_mph <= 75:
        beaufort_number = 11; description = "Storm Force"
    else:
        beaufort_number = 12; description = "Hurricane Force"

    print(f"Wind Speed: {wind_speed_ms:.1f} m/s ")
    print(f"Beaufort Number: {beaufort_number}")
    print(f"Description: {description}")

    return (wind_speed_ms, wind_speed_mph)

def exit():
    return ("Thank you for using, will it rain on my parade!")

# -----------------------------
# ANA DÖNGÜ (MENÜ ETKİLEŞİMİ)
# -----------------------------
choose_option = ""
loc_val = None       # (lat, lon)
date_val = None      # "YYYY-MM-DD"

while choose_option != "7":
    print(menu())
    choose_option = input("Choose your option (1-7): ").strip()

    if choose_option == "1":
        loc_val = location()
    elif choose_option == "2":
        date_val = date()
    elif choose_option == "3":
        if not (loc_val and date_val):
            print("Önce 1) Location ve 2) Date gir.")
        else:
            msg = extreme_temp(date_val, loc_val)  # gerçek veri ile hesap
            print(msg)
    elif choose_option == "4":
        if not (loc_val and date_val):
            print("Önce 1) Location ve 2) Date gir.")
        else:
            p = precipitation_probability(date_val, loc_val)
            print(f"Very wet probability (≥20 mm/day): {p}%")
    elif choose_option == "5":
        uv_index()
    elif choose_option == "6":
        calculate_wind()
    elif choose_option == "7":
        print(exit())
    else:
        print("Invalid choice. Try again!")