import time
import os

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
    lat = float(input("Enter latitude (e.g., 34.05): "))   #Decide later which one
    lon = float(input("Enter longitude (e.g., -118.25): "))
    if -90 <= lat <= 90 and -180 <= lon <= 180:
        print(f"Location set to: Latitude {lat}, Longitude {lon}")
    else:
        print("Warning: Latitude must be -90 to 90 and Longitude must be -180 to 180!")

    return (lat, lon)


def date():
    date = input("Enter the date (YYY-MM-DD) :")
    if len(date) == 10 and date[4] == '-' and date[7] == '-':
        print(f"Date set to: {date}")
    else:
        print("Warning: Date should be in YYYY-MM-DD format!")
    return date
  

def extreme_temp(date, location, avg_temp):
    if avg_temp >= 35:
        return (f"Its very hot! ☀️ The average temp at {location} is {avg_temp}°C.")
    
    elif avg_temp <= -5:
        return (f"Its very hot! 🥶 The average temp at {location} is {avg_temp}°C.")
    else:
        return (f"The conditions at {location} are normal, the temp is {avg_temp}°C.")
    
    

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
    print(extreme_temp(date, location, avg_temp))
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