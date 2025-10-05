from geopy.geocoders import Nominatim
def location():
    # calling the Nominatim tool and create Nominatim class
    loc = Nominatim(user_agent="Geopy Library")

    # entering the location name
    getLoc = loc.geocode(input("Enter your address: "))

    # printing address
    print(getLoc.address)

    # printing latitude and longitude
    print("Latitude = ", getLoc.latitude)
    print("Longitude = ", getLoc.longitude)

    return getLoc.latitude, getLoc.longitude

print(location())