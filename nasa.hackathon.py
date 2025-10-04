import time
import os

def menu():
    return ("""Welcome to will it rain on my parade!
            1. Location
            2. Date
            3. Extreme temperatures
            4. Precipitation probability
            5. UV index
            6. Wind
            7. Exit
            """)

def location():
    city_location = input("Enter the city name")   #Decide later which one
    print(f"City is set to {city_location}")
    return city_location

def date():
    date = input("Enter the date (YYY-MM-DD) :")
    print(f"Date set to :{date}")
    return date

def extreme_temp(date, location):
    pass
def precipitation_probability(date, location):
    probability_precipitation = (n/t) * 100 #just a formula, will change it later
    return probability_precipitation

def uv_index():
    pass

def calculate_wind():
    wind_speed_ms = float(input("Enter wind speed in meters per second(m/s): "))
    wind_speed_mph = wind_speed_ms * 2.2369 

    if wind_speed_mph < 1:
        beaufort_number = 0
        description  = "Calm"
    elif wind_speed_mph >= 1 and wind_speed_mph <= 3:
        beaufort_number = 1 
        description = "Light Air"
    elif wind_speed_mph >= 4 and wind_speed_mph <= 7:
        beaufort_number = 2 
        description = "Light Breeze"
    elif wind_speed_mph >= 8 and wind_speed_mph <= 12:
        beaufort_number = 3 
        description = "Gentle Breeze"
    elif wind_speed_mph >= 13 and wind_speed_mph <= 18:
        beaufort_number = 4
        description = "Moderate Breeze"
    elif wind_speed_mph >= 19 and wind_speed_mph <= 24:
        beaufort_number = 5 
        description = "Fresh Breeze"
    elif wind_speed_mph >= 25 and wind_speed_mph <= 31:
        beaufort_number = 6 
        description = "Strong Breeze"
    elif wind_speed_mph >= 32 and wind_speed_mph <= 38:
        beaufort_number = 7 
        description = "Near Gale"
    elif wind_speed_mph >= 39 and wind_speed_mph <= 46:
        beaufort_number = 8 
        description = "Gale"
    elif wind_speed_mph >= 47 and wind_speed_mph <= 54:
        beaufort_number = 9 
        description = "Strong Gale "
    elif wind_speed_mph >= 55 and wind_speed_mph <= 63:
        beaufort_number = 10 
        description = "Whole Gale"
    elif wind_speed_mph >= 64 and wind_speed_mph <= 75:
        beaufort_number = 11
        description = "Storm Force"
    elif  wind_speed_mph > 75:
        beaufort_number = 12
        description = "Hurricane Force"

    print(f"Wind Speed: {wind_speed_ms:.1f} m/s ")
    print(f"Beaufort Number: {beaufort_number}")
    print(f"Description: {description}")


def exit():
    return ("Thank you for using, will it rain on my parade!")



choose_option = ""

while choose_option != "7":
    print(menu())
    choose_option = input("Choose your option (1-7): ")

if choose_option == "1":
    location = location()
elif choose_option == "2":
    date = date()
elif choose_option == "3":
    extreme_temp(date, location)
elif choose_option == "4":
    precipitation_probability(date, location)
elif choose_option == "5":
    uv_index()
elif choose_option == "6":
    calculate_wind()   
elif choose_option == "7":
    print(exit())
else:
    print("Invalid choice. Try again!")