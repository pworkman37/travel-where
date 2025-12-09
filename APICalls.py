import tkinter as tk
from tkinter import ttk, scrolledtext
from amadeus import Client, ResponseError
import statistics

# ----------------- AMADEUS API KEYS -----------------
AMADEUS_CLIENT_ID = "HOVGmCpH1aiyeCiP4os6GexwellBybIZ"
AMADEUS_CLIENT_SECRET = "o0RPAq66ppyX3IDa"

amadeus = Client(
    client_id=AMADEUS_CLIENT_ID,
    client_secret=AMADEUS_CLIENT_SECRET
)

# Airline names for flight results
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

# ----------------- FLIGHT SEARCH -----------------
def search_flights(origin, destination, depart_date, passengers, limit=20):
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=depart_date,
            adults=passengers,
            max=limit
        )
        data = response.data

        if not data:
            return [], 0, 0, 0

        price_entries = []
        for offer in data[:limit]:
            price = float(offer["price"]["total"])
            airline_code = offer["itineraries"][0]["segments"][0]["carrierCode"]
            airline_name = AIRLINE_NAMES.get(airline_code, airline_code)
            price_entries.append((price, airline_name))

        price_entries.sort(key=lambda x: x[0])
        prices_only = [p[0] for p in price_entries]
        cheapest_price, most_expensive_price = prices_only[0], prices_only[-1]
        median_price = statistics.median(prices_only)

        with open("results.txt", "a") as f:
            f.write("========= FLIGHT PRICES =========\n")
            for i, (price, airline) in enumerate(price_entries):
                f.write(f"{i+1:02d}: ${price:.2f}  {airline}\n")
            f.write(f"\nCheapest Flight: ${cheapest_price:.2f}\n")
            f.write(f"Most Expensive Flight: ${most_expensive_price:.2f}\n")
            f.write(f"Median Flight Price: ${median_price:.2f}\n")
            f.write("==============================\n\n")

        return price_entries, cheapest_price, most_expensive_price, median_price

    except ResponseError as error:
        with open("results.txt", "a") as f:
            f.write(f"Flight API Error: {error}\n")
        return [], 0, 0, 0


# ----------------- HOTEL SEARCH -----------------
def search_hotels(city_input, check_in_date, check_out_date, guests, limit=20):
    try:
        location_response = amadeus.reference_data.locations.hotels.by_city.get(
            cityCode=city_input.upper()
        )
        locations = location_response.data
        if not locations:
            return [], 0, 0, 0

        hotel_ids = [hotel["hotelId"] for hotel in locations[:limit]]  # limit to avoid 414
    except ResponseError as error:
        with open("results.txt", "a") as f:
            f.write(f"Hotel Location API Error: {error}\n")
        return [], 0, 0, 0

    try:
        response = amadeus.shopping.hotel_offers_search.get(
            hotelIds=hotel_ids,
            checkInDate=check_in_date,
            checkOutDate=check_out_date,
            adults=guests,
            roomQuantity=1
        )
        data = response.data
        if not data:
            return [], 0, 0, 0

        price_entries = []
        for offer in data[:limit]:
            hotel_name = offer["hotel"]["name"]
            price = float(offer["offers"][0]["price"]["total"])
            price_entries.append((price, hotel_name))

        price_entries.sort(key=lambda x: x[0])
        prices_only = [p[0] for p in price_entries]
        cheapest_price, most_expensive_price = prices_only[0], prices_only[-1]
        median_price = statistics.median(prices_only)

        with open("results.txt", "a") as f:
            f.write("========= HOTEL PRICES =========\n")
            for i, (price, hotel) in enumerate(price_entries):
                f.write(f"{i+1:02d}: ${price:.2f}  {hotel}\n")
            f.write(f"\nCheapest Hotel: ${cheapest_price:.2f}\n")
            f.write(f"Most Expensive Hotel: ${most_expensive_price:.2f}\n")
            f.write(f"Median Hotel Price: ${median_price:.2f}\n")
            f.write("==============================\n\n")

        return price_entries, cheapest_price, most_expensive_price, median_price

    except ResponseError as error:
        with open("results.txt", "a") as f:
            f.write(f"Hotel API Error: {error}\n")
        return [], 0, 0, 0


# ----------------- GUI -----------------
class TravelWhereGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TravelWhere Flight + Hotel Search")
        self.root.geometry("950x750")

        # --- Flight Info ---
        tk.Label(root, text="Flight Origin (IATA):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.origin_entry = tk.Entry(root, width=20)
        self.origin_entry.grid(row=0, column=1, padx=10)

        tk.Label(root, text="Flight Destination (IATA):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.dest_entry = tk.Entry(root, width=20)
        self.dest_entry.grid(row=1, column=1, padx=10)

        tk.Label(root, text="Departure Date (YYYY-MM-DD):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.depart_entry = tk.Entry(root, width=20)
        self.depart_entry.grid(row=2, column=1, padx=10)

        tk.Label(root, text="Passengers:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.passengers_var = tk.StringVar()
        self.passengers_dropdown = ttk.Combobox(root, textvariable=self.passengers_var, state="readonly", width=18)
        self.passengers_dropdown["values"] = [1, 2, 3, 4, 5, 6, 7, 8]
        self.passengers_dropdown.current(0)
        self.passengers_dropdown.grid(row=3, column=1, padx=10)

        # --- Hotel Info ---
        tk.Label(root, text="Hotel City (IATA):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.city_entry = tk.Entry(root, width=20)
        self.city_entry.grid(row=4, column=1, padx=10)

        tk.Label(root, text="Check-in Date (YYYY-MM-DD):").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.checkin_entry = tk.Entry(root, width=20)
        self.checkin_entry.grid(row=5, column=1, padx=10)

        tk.Label(root, text="Check-out Date (YYYY-MM-DD):").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.checkout_entry = tk.Entry(root, width=20)
        self.checkout_entry.grid(row=6, column=1, padx=10)

        tk.Label(root, text="Guests:").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        self.guests_var = tk.StringVar()
        self.guests_dropdown = ttk.Combobox(root, textvariable=self.guests_var, state="readonly", width=18)
        self.guests_dropdown["values"] = [1, 2, 3, 4, 5, 6, 7, 8]
        self.guests_dropdown.current(0)
        self.guests_dropdown.grid(row=7, column=1, padx=10)

        # Search button
        self.search_button = tk.Button(root, text="Search Flight + Hotel", command=self.perform_search, width=30)
        self.search_button.grid(row=8, column=0, columnspan=2, pady=15)

        # Results box
        self.results_box = scrolledtext.ScrolledText(root, width=110, height=30)
        self.results_box.grid(row=9, column=0, columnspan=3, padx=10, pady=10)

    def perform_search(self):
        with open("results.txt", "w") as f:
            f.write("")

        origin = self.origin_entry.get().strip().upper()
        destination = self.dest_entry.get().strip().upper()
        depart_date = self.depart_entry.get().strip()
        passengers = int(self.passengers_var.get())

        city_code = self.city_entry.get().strip().upper()
        check_in = self.checkin_entry.get().strip()
        check_out = self.checkout_entry.get().strip()
        guests = int(self.guests_var.get())

        self.results_box.delete(1.0, tk.END)
        self.results_box.insert(tk.END, "Searching flights and hotels...\n")

        flight_entries, flight_cheapest, flight_expensive, flight_median = search_flights(
            origin, destination, depart_date, passengers
        )
        hotel_entries, hotel_cheapest, hotel_expensive, hotel_median = search_hotels(
            city_code, check_in, check_out, guests
        )

        self.results_box.delete(1.0, tk.END)
        self.results_box.insert(tk.END, "Search complete — results saved to results.txt\n\n")

        self.results_box.insert(tk.END, "----- Flights -----\n")
        for price, airline in flight_entries:
            self.results_box.insert(tk.END, f"${price:.2f} — {airline}\n")
        self.results_box.insert(tk.END, f"\nCheapest: ${flight_cheapest:.2f}, Most Expensive: ${flight_expensive:.2f}, Median: ${flight_median:.2f}\n\n")

        self.results_box.insert(tk.END, "----- Hotels -----\n")
        for price, hotel in hotel_entries:
            self.results_box.insert(tk.END, f"${price:.2f} — {hotel}\n")
        self.results_box.insert(tk.END, f"\nCheapest: ${hotel_cheapest:.2f}, Most Expensive: ${hotel_expensive:.2f}, Median: ${hotel_median:.2f}\n")


# ----------------- RUN APP -----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TravelWhereGUI(root)
    root.mainloop()
