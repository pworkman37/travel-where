import tkinter as tk
from tkinter import ttk, scrolledtext
from amadeus import Client, ResponseError

# ------------------------------------------------------
# SET YOUR AMADEUS API KEYS HERE
# ------------------------------------------------------
AMADEUS_CLIENT_ID = "HOVGmCpH1aiyeCiP4os6GexwellBybIZ"
AMADEUS_CLIENT_SECRET = "o0RPAq66ppyX3IDa"

amadeus = Client(
    client_id=AMADEUS_CLIENT_ID,
    client_secret=AMADEUS_CLIENT_SECRET
)

# Airline name lookup (fallback if coding missing)
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

# ------------------------------------------------------
# AMADEUS FLIGHT SEARCH FUNCTION
# ------------------------------------------------------
def search_flights(origin, destination, depart_date, return_date, passengers):
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=depart_date,
            returnDate=return_date,
            adults=passengers,
            max=40
        )

        data = response.data

        # Store offers grouped by airline
        airline_offers = {}
        all_prices = set()  # UNIQUE prices only

        for offer in data:
            price = float(offer["price"]["total"])
            all_prices.add(price)  # ensure uniqueness

            airline_code = offer["itineraries"][0]["segments"][0]["carrierCode"]
            airline_name = AIRLINE_NAMES.get(airline_code, airline_code)

            if airline_name not in airline_offers:
                airline_offers[airline_name] = []

            airline_offers[airline_name].append({
                "price": price,
                "offer": offer
            })

        # Sort unique prices for terminal summary
        all_prices = sorted(all_prices)

        # ------------------------------------------------------
        # TERMINAL OUTPUT — unique prices summary
        # ------------------------------------------------------
        if all_prices:
            cheapest = all_prices[0]
            most_expensive = all_prices[-1]
            average = sum(all_prices) / len(all_prices)

            print("========= UNIQUE PRICE SUMMARY =========")
            print(f"Unique Prices Found: {len(all_prices)}")
            print(f"Cheapest Flight:      ${cheapest:.2f}")
            print(f"Average Flight:       ${average:.2f}")
            print(f"Most Expensive:       ${most_expensive:.2f}")
            print("========================================")
        else:
            print("No flight prices returned.")

        # ------------------------------------------------------
        # Build GUI output (cheapest + most expensive per airline)
        # x------------------------------------------------------
        results = []

        for airline, offers in airline_offers.items():
            offers_sorted = sorted(offers, key=lambda x: x["price"])

            cheapest_offer = offers_sorted[0]
            expensive_offer = offers_sorted[-1]

            results.append(
                f"{airline} — Cheapest: ${cheapest_offer['price']:.2f}"
            )
            results.append(
                f"{airline} — Most Expensive: ${expensive_offer['price']:.2f}"
            )
            results.append("-----------------------------")

        if not results:
            return "No flights found."

        return "\n".join(results)

    except ResponseError as error:
        return f"API Error: {error}"


# ------------------------------------------------------
# GUI APPLICATION
# ------------------------------------------------------
class TravelWhereGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TravelWhere Flight Search")
        self.root.geometry("950x700")

        tk.Label(root, text="From (IATA):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.from_entry = tk.Entry(root, width=20)
        self.from_entry.grid(row=0, column=1, padx=10)

        tk.Label(root, text="To (IATA):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.to_entry = tk.Entry(root, width=20)
        self.to_entry.grid(row=1, column=1, padx=10)

        tk.Label(root, text="Depart Date (YYYY-MM-DD):").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.depart_entry = tk.Entry(root, width=20)
        self.depart_entry.grid(row=2, column=1, padx=10)

        tk.Label(root, text="Return Date (YYYY-MM-DD):").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.return_entry = tk.Entry(root, width=20)
        self.return_entry.grid(row=3, column=1, padx=10)

        # Passenger dropdown
        tk.Label(root, text="Passengers:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.passengers_var = tk.StringVar()
        self.passengers_dropdown = ttk.Combobox(
            root, textvariable=self.passengers_var, state="readonly", width=18
        )
        self.passengers_dropdown["values"] = [1, 2, 3, 4, 5, 6, 7, 8]
        self.passengers_dropdown.current(0)
        self.passengers_dropdown.grid(row=4, column=1, padx=10)

        self.search_button = tk.Button(root, text="Search Flights", command=self.perform_search, width=20)
        self.search_button.grid(row=5, column=0, columnspan=2, pady=20)

        self.results_box = scrolledtext.ScrolledText(root, width=110, height=25)
        self.results_box.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

    def perform_search(self):
        origin = self.from_entry.get().strip().upper()
        destination = self.to_entry.get().strip().upper()
        depart_date = self.depart_entry.get().strip()
        return_date = self.return_entry.get().strip()
        passengers = int(self.passengers_var.get())

        self.results_box.delete(1.0, tk.END)
        self.results_box.insert(tk.END, "Searching Amadeus...\n")

        results = search_flights(origin, destination, depart_date, return_date, passengers)

        self.results_box.delete(1.0, tk.END)
        self.results_box.insert(tk.END, results)


# ------------------------------------------------------
# RUN APP
# ------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TravelWhereGUI(root)
    root.mainloop()
