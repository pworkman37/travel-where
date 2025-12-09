from flask import Flask, render_template, request
from amadeus import Client, ResponseError
import statistics

app = Flask(__name__)

# ----------------- AMADEUS API KEYS -----------------
AMADEUS_CLIENT_ID = "HOVGmCpH1aiyeCiP4os6GexwellBybIZ"
AMADEUS_CLIENT_SECRET = "o0RPAq66ppyX3IDa"

amadeus = Client(
    client_id=AMADEUS_CLIENT_ID,
    client_secret=AMADEUS_CLIENT_SECRET
)

# Airline codes to names
AIRLINE_NAMES = {
    "AA": "American Airlines",
    "DL": "Delta Air Lines",
    "UA": "United Airlines",
    "F9": "Frontier",
    "NK": "Spirit",
    "AS": "Alaska Airlines",
    "B6": "JetBlue",
    "WN": "Southwest",
    "HA": "Hawaiian Airlines"
}

# City names to IATA codes for hotels
CITY_TO_IATA = {
    "London": "LON",
    "New York": "NYC"
}

# ----------------- FLIGHTS -----------------
def search_flights(origin, destination, depart_date, passengers, limit=20):
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=depart_date,
            adults=passengers,
            max=limit
        )
        data = response.data or []

        price_entries = []
        for offer in data[:limit]:
            price = float(offer["price"]["total"])
            airline_code = offer["itineraries"][0]["segments"][0]["carrierCode"]
            airline_name = AIRLINE_NAMES.get(airline_code, airline_code)
            price_entries.append((price, airline_name))

        if not price_entries:
            return {}

        # Sort prices
        price_entries.sort(key=lambda x: x[0])
        prices_only = [p[0] for p in price_entries]

        # Median entry
        median_price = statistics.median(prices_only)
        median_entry = min(price_entries, key=lambda x: abs(x[0]-median_price))

        return {
            "cheapest": price_entries[0],
            "most_expensive": price_entries[-1],
            "median": median_entry
        }
    except ResponseError:
        return {}

# ----------------- HOTELS -----------------
def search_hotels(city_name, check_in, check_out, guests, limit=20):
    city_code = CITY_TO_IATA.get(city_name.title())
    if not city_code:
        return {}

    try:
        response = amadeus.shopping.hotel_offers.get(
            cityCode=city_code,
            checkInDate=check_in,
            checkOutDate=check_out,
            adults=guests,
            roomQuantity=1,
            max=limit
        )
        data = response.data or []

        price_entries = []
        for offer in data[:limit]:
            hotel_name = offer["hotel"]["name"]
            price = float(offer["offers"][0]["price"]["total"])
            price_entries.append((price, hotel_name))

        if not price_entries:
            return {}

        price_entries.sort(key=lambda x: x[0])
        prices_only = [p[0] for p in price_entries]
        median_price = statistics.median(prices_only)
        median_entry = min(price_entries, key=lambda x: abs(x[0]-median_price))

        return {
            "cheapest": price_entries[0],
            "most_expensive": price_entries[-1],
            "median": median_entry
        }

    except ResponseError:
        return {}

# ----------------- FLASK ROUTE -----------------
@app.route("/", methods=["GET", "POST"])
def index():
    flight_results = {}
    hotel_results = {}
    if request.method == "POST":
        origin = request.form["origin"].strip().upper()
        destination = request.form["destination"].strip().upper()
        depart_date = request.form["depart_date"].strip()
        passengers = int(request.form["passengers"])

        hotel_city = request.form["hotel_city"].strip()
        checkin = request.form["checkin"].strip()
        checkout = request.form["checkout"].strip()
        guests = int(request.form["guests"])

        flight_results = search_flights(origin, destination, depart_date, passengers)
        hotel_results = search_hotels(hotel_city, checkin, checkout, guests)

    return render_template("results.html",
                           flight_results=flight_results,
                           hotel_results=hotel_results)

if __name__ == "__main__":
    app.run(debug=True)
