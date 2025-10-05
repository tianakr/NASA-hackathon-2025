import requests as req
import json
from datetime import datetime, date
from geopy.geocoders import Nominatim
import calendar
import math

# ---------- ASK LOCATION ----------

def ask_location():
    geocoder = Nominatim(user_agent="Geopy Library")
    getLoc = geocoder.geocode(input("Enter your address: "))
    if not getLoc:
        print("⚠️  Sorry, I couldn't find that address. Try something more specific.")
        return None
    print(getLoc.address)
    print("Latitude =", getLoc.latitude)
    print("Longitude =", getLoc.longitude)
    return (getLoc.latitude, getLoc.longitude)


# ---------- ASK DATE ----------

def ask_date():
    s = input("Enter the date (YYYY-MM-DD): ").strip()
    try:
        end_date = datetime.strptime(s, "%Y-%m-%d").date()
        print(f"✅ Date set to: {end_date}")
    except ValueError:
        print("⚠️  Warning: Date should be in YYYY-MM-DD format!")
        s = input("Enter the date (YYYY-MM-DD): ").strip()
        end_date = datetime.strptime(s, "%Y-%m-%d").date()

    past_dates = []
    for i in range(1, 11):
        y, m, d = end_date.year - i, end_date.month, end_date.day
        # handle Feb 29 → Mar 1 on non-leap years
        if m == 2 and d == 29 and not calendar.isleap(y):
            d, m = 1, 3
        past_dates.append(date(y, m, d))
    return end_date, past_dates


# ---------- NASA POWER ----------

def power_daily_url(user_data, day):
    lat, lon = user_data["Location"]
    params = user_data["Params"]
    ymd = day.strftime("%Y%m%d")
    return (
        "https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?start={ymd}&end={ymd}"
        f"&latitude={lat}&longitude={lon}"
        f"&community=re&parameters={params}"
        "&format=json&units=metric&header=true"
    )


def fetch_daily_means_for_dates(user_data):
    """
    For each date in user_data['Past_dates'], fetch T2M, T2M_MAX, T2M_MIN.
    Returns list of tuples: (day, t2m_mean, t2m_max, t2m_min) with None if missing.
    """
    results = []

    for day in user_data["Past_dates"]:
        url = power_daily_url(user_data, day)
        try:
            response = req.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()

            parameters = data.get("properties", {}).get("parameter", {})
            key = day.strftime("%Y%m%d")

            def to_float(x):
                try:
                    return float(x)
                except (TypeError, ValueError):
                    return None

            t2m     = to_float(parameters.get("T2M", {}).get(key))
            t2m_max = to_float(parameters.get("T2M_MAX", {}).get(key))
            t2m_min = to_float(parameters.get("T2M_MIN", {}).get(key))

            results.append((day, t2m, t2m_max, t2m_min))

        except req.RequestException as e:
            print(f"⚠️  Network/API error for {day}: {e}")
            results.append((day, None, None, None))
        except json.JSONDecodeError:
            print(f"⚠️  Could not parse response for {day}")
            results.append((day, None, None, None))

    return results


def compute_daily_mean(t2m_mean, t2m_max, t2m_min):
    # Best available daily mean
    if t2m_mean is not None:
        return t2m_mean
    if t2m_max is not None and t2m_min is not None:
        return (t2m_max + t2m_min) / 2.0
    return None


def temp_data(user_data):
    """
    Uses NASA POWER (daily) to fetch last-10-year same-day temps
    and reports likelihood of >=35°C and <= -5°C.
    """
    if not user_data.get("Location") or not user_data.get("Date") or not user_data.get("Past_dates"):
        return "⚠️ Please set location and date first!"

    lat, lon = user_data["Location"]
    target_day = user_data["Date"]

    results = fetch_daily_means_for_dates(user_data)

    daily_means = []
    missing = 0
    for day, t2m, tmax, tmin in results:
        mean_val = compute_daily_mean(t2m, tmax, tmin)
        if mean_val is None:
            missing += 1
        else:
            daily_means.append((day, mean_val))

    if not daily_means:
        return "⚠️ Could not compute any daily means for the past 10 years. Try a different location or date."

    n = len(daily_means)
    hot_count  = sum(1 for _, m in daily_means if m >= 35.0)
    cold_count = sum(1 for _, m in daily_means if m <= -5.0)

    hot_pct  = round(hot_count  / n * 100, 1)
    cold_pct = round(cold_count / n * 100, 1)
    avg_of_means = round(sum(m for _, m in daily_means) / n, 1)

    lines = []
    lines.append(
        f"📍 Location: lat {lat:.4f}, lon {lon:.4f}\n"
        f"📅 Target day: {target_day} (using same calendar day for the last 10 years)"
    )
    if missing > 0:
        lines.append(f"ℹ️  {missing} of 10 historical days had incomplete data and were skipped.")
    lines.append(
        f"🌡️  Average of daily means across history: {avg_of_means} °C\n"
        f"🔥 Likelihood of ≥ 35 °C: {hot_pct}%  ({hot_count}/{n} years)\n"
        f"❄️  Likelihood of ≤ -5 °C: {cold_pct}%  ({cold_count}/{n} years)\n"
        f"🗓️  Historical dates used: {', '.join(d.strftime('%Y-%m-%d') for d, _ in daily_means)}"
    )

    threshold = math.ceil(0.5 * n)  # at least 50% of the available years

    if hot_count >= threshold and hot_count > cold_count:
        return (
            f"Its likely to be very hot! ☀️ Based on {n} past years for this date, "
            f"{hot_pct}% were ≥ 35 °C."
        )
    elif cold_count >= threshold and cold_count > hot_count:
        return (
            f"Its very cold! 🥶 Based on {n} past years for this date, "
            f"{cold_pct}% were ≤ -5 °C."
        )
    else:
        return f"The conditions look normal. Average daily temp is {avg_of_means} °C."


user_data = {
    "Location": None,
    "Date": None,
    "Past_dates": None,
    "Params": "T2M,T2M_MAX,T2M_MIN"
}

loc = ask_location()
if loc:
    user_data["Location"] = loc

result = ask_date()
if result:
    user_data["Date"], user_data["Past_dates"] = result

if user_data["Location"] and user_data["Date"]:
    print(temp_data(user_data))
else:
    print("⚠️ Please set location and date first!")