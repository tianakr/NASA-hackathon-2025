import requests as req
import json
from datetime import datetime, timedelta, date
from geopy.geocoders import Nominatim
import calendar


def menu():
    return ("""Welcome to will it rain on my parade!
            1. Location
            2. Date
            3. Extreme temp
            5. Precipitation probability
            6. UV index
            7. Wind
            9. Exit
            """)


def ask_location():
    # Create a Nominatim geocoder
    loc = Nominatim(user_agent="Geopy Library")

    # Ask user and geocode
    getLoc = loc.geocode(input("Enter your address: "))

    if not getLoc:
        print("⚠️  Sorry, I couldn't find that address. Try something more specific.")
        return None

    # Print address and coordinates
    print(getLoc.address)
    print("Latitude = ", getLoc.latitude)
    print("Longitude = ", getLoc.longitude)
    
    # Return (lat, lon) tuple
    return (getLoc.latitude, getLoc.longitude)


def ask_date():
    user_input = input("Enter the date (YYYY-MM-DD): ").strip()

    # Validate the input format
    try:
        end_date = datetime.strptime(user_input, "%Y-%m-%d").date()
        print(f"✅ Date set to: {end_date}")
    except ValueError:
        print("⚠️  Warning: Date should be in YYYY-MM-DD format!")
        user_input = input("Enter the date (YYYY-MM-DD): ").strip()
        end_date = datetime.strptime(user_input, "%Y-%m-%d").date()

    # Create list of the same calendar day for the last 10 years
    past_dates = []
    for i in range(1, 11): 
        year = end_date.year - i
        month = end_date.month
        day = end_date.day

        # Handle leap-year Feb 29 → use Mar 1 on non-leap years
        if month == 2 and day == 29 and not calendar.isleap(year):
            day = 1
            month = 3

        past_dates.append(date(year, month, day))

    return end_date, past_dates


# -------- NASA POWER integration (daily) --------

def _power_daily_url(lat: float, lon: float, the_date: date, params: str) -> str:
    """
    Build NASA POWER daily endpoint URL for a single day (start=end=this date).
    """
    ymd = the_date.strftime("%Y%m%d")
    return (
        "https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?start={ymd}&end={ymd}"
        f"&latitude={lat}&longitude={lon}"
        f"&community=re&parameters={params}"
        "&format=json&units=metric&header=true"
    )


def _fetch_daily_means_for_dates(lat: float, lon: float, dates: list[date]) -> list[tuple[date, float | None, float | None, float | None]]:
    """
    For each date, fetch T2M (daily mean), T2M_MAX, T2M_MIN from NASA POWER daily API.

    Returns a list of tuples: (date, t2m_mean, t2m_max, t2m_min)
    Any missing value will be None for that field on that date.
    """
    out = []
    params = "T2M,T2M_MAX,T2M_MIN"

    for d in dates:
        url = _power_daily_url(lat, lon, d, params)
        try:
            r = req.get(url, timeout=20)
            r.raise_for_status()
            data = r.json()

            p = data.get("properties", {}).get("parameter", {})
            key = d.strftime("%Y%m%d")

            t2m = p.get("T2M", {}).get(key)
            t2m_max = p.get("T2M_MAX", {}).get(key)
            t2m_min = p.get("T2M_MIN", {}).get(key)

            # Coerce to float when possible
            def _to_float(x):
                try:
                    return float(x)
                except (TypeError, ValueError):
                    return None

            out.append((d, _to_float(t2m), _to_float(t2m_max), _to_float(t2m_min)))

        except req.RequestException as e:
            print(f"⚠️  Network/API error for {d}: {e}")
            out.append((d, None, None, None))
        except json.JSONDecodeError:
            print(f"⚠️  Could not parse response for {d}")
            out.append((d, None, None, None))

    return out


def _compute_daily_mean(t2m_mean, t2m_max, t2m_min):
    """
    Decide the best available daily mean for a day:
    1) If T2M (daily mean) is present, use it.
    2) Else if both max/min exist, use (max + min) / 2.
    3) Else return None.
    """
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
    if not user_data["location"] or not user_data["end_date"] or not user_data["past_dates"]:
        return "⚠️ Please set location and date first!"

    lat, lon = user_data["location"]
    target_day = user_data["end_date"]
    history_days = user_data["past_dates"]

    # Fetch daily data for the 10 historical same-days
    results = _fetch_daily_means_for_dates(lat, lon, history_days)

    daily_means = []
    missing = 0
    for d, t2m, tmax, tmin in results:
        mean_val = _compute_daily_mean(t2m, tmax, tmin)
        if mean_val is None:
            missing += 1
        else:
            daily_means.append((d, mean_val))

    if len(daily_means) == 0:
        return "⚠️ Could not compute any daily means for the past 10 years. Try a different location or date."

    # Compute likelihoods
    hot_count = sum(1 for _, m in daily_means if m >= 35.0)
    cold_count = sum(1 for _, m in daily_means if m <= -5.0)
    n = len(daily_means)

    hot_pct = round((hot_count / n) * 100, 1)
    cold_pct = round((cold_count / n) * 100, 1)
    avg_of_means = round(sum(m for _, m in daily_means) / n, 1)

    # Build a friendly summary
    date_list_str = ", ".join(d.strftime("%Y-%m-%d") for d, _ in daily_means)

    lines = []
    lines.append(f"""
                 📍 Location: lat {lat:.4f}, lon {lon:.4f}")
                📅 Target day: {target_day} (using same calendar day for the last 10 years)
                """)
    if missing > 0:
        lines.append(f"""
                ℹ️  {missing} of 10 historical days had incomplete data and were skipped.
                🌡️  Average of daily means across history: {avg_of_means} °C")
                🔥 Likelihood of ≥ 35 °C: {hot_pct}%  ({hot_count}/{n} years)")
                ❄️  Likelihood of ≤ -5 °C: {cold_pct}%  ({cold_count}/{n} years)")
                🗓️  Historical dates used: {date_list_str}
                """)

    # Also return one-liner like your original structure
    if hot_count > cold_count and hot_count > 0:
        headline = f"Its likely to be very hot! ☀️ Based on {n} past years for this date, {hot_pct}% were ≥ 35 °C."
    elif cold_count > hot_count and cold_count > 0:
        headline = f"Its very cold! 🥶 Based on {n} past years for this date, {cold_pct}% were ≤ -5 °C."
    else:
        headline = f"The conditions look normal. Average daily mean is {avg_of_means} °C."

    return headline + "\n" + "\n".join(lines)


def exit():
    return ("Thank you for using will it rain on my parade") 


user_choice = ""
user_data = {
    "location": None,   # (lat, lon)
    "end_date": None,   # date chosen by user
    "past_dates": None, # list of 10 historical same-day dates
    "timezone": None
}

while user_choice != "9":
    print(menu())
    user_choice = input("Choose your option (1-9): ").strip()

    if user_choice == "1":
        loc = ask_location()
        if loc:
            user_data["location"] = loc

    elif user_choice == "2":
        result = ask_date()
        if result:
            user_data["end_date"], user_data["past_dates"] = result
    
    elif user_choice == "3":
        if user_data["location"] and user_data["end_date"]:
            print(temp_data(user_data))
        else:
            print("⚠️ Please set location and date first!")

    elif user_choice == "9":
        print(exit())
