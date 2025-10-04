import time
import os

def menu():
    return ("""Welcome to will it rain on my parade!
            1. Location
            2. Date
            3. Extreme temperatures
            4. Rain probability
            5. Exit
            """)

def location():
    
def date():

def extreme_temp(date, location):

def rain_probability(date, location):

def exit():
    return ("Thamk you for using, will it rain on my parade! 🌦️")



choose_option = ""

while choose_option != 5:
    print(menu())
    choose_option = input("Choose your option (1-5): ")

if choose_option == "1":
    location = location()
elif choose_option == "2":
    date = date()
elif choose_option == "3":
    extreme_temp(date, location)
elif choose_option == "4":
    rain_probability(date, location)
elif choose_option == "5":
    print(exit())