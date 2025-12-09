import random
import statistics
import math
from flask import Flask, render_template, request
from amadeus import Client, ResponseError

app = Flask(__name__)

#AMADEUS TEST KEYS
AMADEUS_CLIENT_ID = "HOVGmCpH1aiyeCiP4os6GexwellBybIZ"
AMADEUS_CLIENT_SECRET = "o0RPAq66ppyX3IDa"

amadeus = Client(
    client_id=AMADEUS_CLIENT_ID,
    client_secret=AMADEUS_CLIENT_SECRET
)

#AIRLINE CODES to English in a dict
AIRLINE_NAMES = {
    "AA": "American Airlines",
    "DL": "Delta Air Lines",
    "UA": "United Airlines",
    "F9": "Frontier Airlines",
    "NK": "Spirit Airlines",
    "AS": "Alaska Airlines",
    "B6": "JetBlue Airways",
    "WN": "Southwest Airlines",
    "HA": "Hawaiian Airlines",
    "TP": "TAP Air Portugal",
    "FI": "Icelandair",
    "AC": "Air Canada",
    "AF": "Air France",
    "BA": "British Airways",
    "LH": "Lufthansa",
    "EK": "Emirates",
    "QR": "Qatar Airways",
    "SQ": "Singapore Airlines",
    "KL": "KLM Royal Dutch Airlines",
    "CX": "Cathay Pacific",
    "NH": "All Nippon Airways (ANA)",
    "JL": "Japan Airlines",
    "IB": "Iberia",
    "AZ": "Alitalia / ITA Airways",
    "EY": "Etihad Airways",
    "MS": "EgyptAir",
    "SK": "Scandinavian Airlines",
    "SU": "Aeroflot",
    "CZ": "China Southern Airlines",
    "MU": "China Eastern Airlines",
    "QF": "Qantas Airways"
}


#CITY to Airport Code
CITY_TO_IATA = {
    "New York": "NYC",   
    "Los Angeles": "LAX",
    "Chicago": "CHI",    
    "San Francisco": "SFO",
    "Miami": "MIA",
    "Boston": "BOS",
    "Dallas": "DFW",
    "Atlanta": "ATL",
    "Seattle": "SEA",
    "Washington DC": "WAS",  
    "London": "LON",          
    "Paris": "PAR",           
    "Berlin": "BER",
    "Madrid": "MAD",
    "Rome": "ROM",            
    "Tokyo": "TYO",           
    "Osaka": "OSA",
    "Beijing": "BJS",         
    "Shanghai": "SHA",
    "Singapore": "SIN",
    "Hong Kong": "HKG",
    "Dubai": "DXB",
    "Istanbul": "IST",
    "Sydney": "SYD",
    "Melbourne": "MEL",
    "Toronto": "YTO",        
    "Vancouver": "YVR",
    "Montreal": "YMQ",       
    "Rio de Janeiro": "GIG",
    "Sao Paulo": "GRU",
    "Cape Town": "CPT",
    "Johannesburg": "JNB",
    "Moscow": "MOW",         
    "Amsterdam": "AMS",
    "Lisbon": "LIS",
    "Dublin": "DUB"
}


# ----------------- FLIGHT SEARCH -----------------
def search_flights(origin, destination, depart_date, passengers, limit=20):
    try:
        #Amadeus call format found on their website
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=depart_date.strip(),
            adults=passengers,
            max=limit
        )

        #Where the data from Amadeus goes and each unique price point
        data = response.data or []
        price_entries = []

        for offer in data:
            #iterates through data to make a list of prices to calculate options later
            #exception handling for multiple problems that may occur during this process
            try:
                price = float(offer["price"]["total"])
                airline_code = offer["itineraries"][0]["segments"][0]["carrierCode"]
                airline_name = AIRLINE_NAMES.get(airline_code, airline_code)
                price_entries.append((price, airline_name))
            except (KeyError, TypeError, ValueError):
                continue
        #if no prices/flights return an empty list
        if not price_entries:
            return {}

        #sorts prices from high to low to calculate the cheapest, median, and most expensive flight prices
        price_entries.sort(key=lambda x: x[0])
        prices_only = [p[0] for p in price_entries]

        #gathers median price
        median_price = statistics.median(prices_only)
        median_entry = min(price_entries, key=lambda x: abs(x[0] - median_price))

        #outputs prices using the price entries dictionary holding price and airline code
        return {
            "cheapest": {"price": price_entries[0][0], "airline": price_entries[0][1]},
            "most_expensive": {"price": price_entries[-1][0], "airline": price_entries[-1][1]},
            "median": {"price": median_entry[0], "airline": median_entry[1]}
        }

    except ResponseError as e:
        print("Flight API ERROR:", e)
        return {}

# ----------------- SIMULATED HOTEL SEARCH -----------------
# List of real hotel brands
HOTEL_BRANDS = [
    "Hilton", "Marriott", "Hyatt", "Sheraton", "Holiday Inn",
    "InterContinental", "Radisson", "Westin", "Four Seasons", "JW Marriott"
]

def search_hotels_simulated(city_name, check_in, check_out, guests, limit=5):
    """
    Simulate hotels with real brand names + city, scaling price per room (2 guests per room)
    and per night.
    """

    #Formats city name so no matter entry always looks presentable
    city_name = city_name.title()
    #generates 5 different hotels to compare prices from 
    hotels = [f"{HOTEL_BRANDS[i % len(HOTEL_BRANDS)]} {city_name}" for i in range(limit)]

    # Calculate number of nights from check-in/check-out
    in_day = int(check_in.split("-")[-1])
    out_day = int(check_out.split("-")[-1])
    nights = max(1, out_day - in_day)

    price_entries = []
    for hotel in hotels:
        # Rooms needed for 2 guests per room
        rooms_needed = math.ceil(guests / 2)
        # Base price per night per room
        base_price = 200 + random.randint(20, 200)
        # to get total price
        total_price = base_price * nights * rooms_needed
        # add total price of specific hotel to the list
        price_entries.append((total_price, hotel))

    # Sort by price
    price_entries.sort(key=lambda x: x[0])
    prices_only = [p[0] for p in price_entries]

    #get median price from list for output
    median_price = statistics.median(prices_only)
    median_entry = min(price_entries, key=lambda x: abs(x[0] - median_price))

    return {
        "cheapest": {"price": price_entries[0][0], "hotel": price_entries[0][1]},
        "most_expensive": {"price": price_entries[-1][0], "hotel": price_entries[-1][1]},
        "median": {"price": median_entry[0], "hotel": median_entry[1]}
    }


# ----------------- FLASK ROUTE -----------------
@app.route("/", methods=["GET", "POST"])
def index():
    flight_results = {}
    hotel_results = {}
    bundles = {}

    #gathers information from text boxes on the website to use in the search functions
    if request.method == "POST":
        origin = request.form.get("origin", "").strip().upper()
        destination = request.form.get("destination", "").strip().upper()
        depart_date = request.form.get("depart_date", "")
        passengers = int(request.form.get("passengers", 1))

        hotel_city = request.form.get("hotel_city", "")
        checkin = request.form.get("checkin", "")
        checkout = request.form.get("checkout", "")
        guests = int(request.form.get("guests", 1))

        #Search function call with parameters provided by the user
        flight_results = search_flights(origin, destination, depart_date, passengers)
        hotel_results = search_hotels_simulated(hotel_city, checkin, checkout, guests, limit=5)

        # ----------------- Create Bundles -----------------
        if flight_results and hotel_results:
            bundles = {
                "cheapest": {
                    "total_price": flight_results["cheapest"]["price"] + hotel_results["cheapest"]["price"],
                    "flight": flight_results["cheapest"],
                    "hotel": hotel_results["cheapest"]
                },
                "median": {
                    "total_price": flight_results["median"]["price"] + hotel_results["median"]["price"],
                    "flight": flight_results["median"],
                    "hotel": hotel_results["median"]
                },
                "most_expensive": {
                    "total_price": flight_results["most_expensive"]["price"] + hotel_results["most_expensive"]["price"],
                    "flight": flight_results["most_expensive"],
                    "hotel": hotel_results["most_expensive"]
                }
            }

    return render_template(
        "Website.html",
        flight_results=flight_results,
        hotel_results=hotel_results,
        bundles=bundles
    )

#Run APP
if __name__ == "__main__":
    app.run(debug=True)
