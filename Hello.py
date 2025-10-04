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
    
def date():

def extreme_conditions(date, location avg_temg, wind, percipitation):
    if avg_temp >= 35:
        return (f"Its very hot! ☀️ The average temp at {location} is {avg_temp}°C.")
    
    elif avg_temp <= -5:
        return (f"Its very hot! 🥶 The average temp at {location} is {avg_temp}°C.")
    
    elif wind >= 8:
        return (f"Its very windy! 💨 The average wind speed at {location} is {wind}m/s.")
    
    elif percipitation >= 10:
        return (f"Its very wet! 🌧️ The average rainfall at {location} is {percipitation}")



def precipitation_probability(date, location):
    probability_precipitation = (n/t) * 100 #just a formula, will change it later
    return probability_precipitation

def uv_index():

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
    precipitation_probability()   
elif choose_option == "7":
    print(exit())
else:
    print("Invalid choice. Try again!")