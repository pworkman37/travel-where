import tkinter as tk
from tkinter import ttk, scrolledtext
import requests

# ---------- CONFIG ----------
XOTELO_BASE = "https://data.xotelo.com/api"
HEADERS = {}  # Add API key header here if required

# ---------- FUNCTIONS ----------
def search_hotels(city_name, check_in, check_out, adults=1, limit=20):
    """
    Automates hotel search by city using Xotelo.
    Returns a list of hotels with price and provider + summary of prices.
    """
    # 1) Search hotels by city name
    try:
        resp = requests.get(
            f"{XOTELO_BASE}/search",
            params={"query": city_name},
            headers=HEADERS,
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        hotels = data.get("result", {}).get("list", [])
        if not hotels:
            return [], None
    except Exception as e:
        return [], f"Error searching hotels: {e}"

    results = []
    unique_prices = set()

    # 2) Fetch rates for top hotels
    for hotel in hotels[:limit]:
        hotel_key = hotel.get("hotel_key")
        name = hotel.get("name", "Unknown Hotel")
        if not hotel_key:
            continue

        try:
            rates_resp = requests.get(
                f"{XOTELO_BASE}/rates",
                params={
                    "hotel_key": hotel_key,
                    "chk_in": check_in,
                    "chk_out": check_out,
                    "adults": adults,
                    "currency": "USD"
                },
                headers=HEADERS,
                timeout=10
            )
            rates_resp.raise_for_status()
            rates_data = rates_resp.json()
            rates = rates_data.get("result", {}).get("rates", [])

            for r in rates:
                price = r.get("rate")
                provider = r.get("name", r.get("code", "Unknown"))
                if price:
                    unique_prices.add(price)
                    results.append({
                        "hotel_name": name,
                        "price": price,
                        "provider": provider
                    })
        except Exception as e:
            print(f"Error fetching rates for {name}: {e}")
            continue

    # 3) Compute summary
    summary = None
    if unique_prices:
        sorted_prices = sorted(unique_prices)
        summary = {
            "cheapest": sorted_prices[0],
            "most_expensive": sorted_prices[-1],
            "average": sum(sorted_prices)/len(sorted_prices),
            "count": len(sorted_prices)
        }

    return results, summary

# ---------- GUI ----------
class HotelWhereXoteloGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HotelWhere (Xotelo) Search")
        self.root.geometry("900x650")

        # Input fields
        tk.Label(root, text="City Name:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.city_entry = tk.Entry(root, width=40)
        self.city_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(root, text="Check-in (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.checkin_entry = tk.Entry(root, width=20)
        self.checkin_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(root, text="Check-out (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.checkout_entry = tk.Entry(root, width=20)
        self.checkout_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(root, text="Adults:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.adults_var = tk.StringVar(value="1")
        self.adults_combo = ttk.Combobox(root, textvariable=self.adults_var, values=[str(i) for i in range(1,6)], width=5)
        self.adults_combo.grid(row=3, column=1, sticky="w", padx=10, pady=5)

        search_btn = tk.Button(root, text="Search Hotels", command=self.perform_search)
        search_btn.grid(row=4, column=0, columnspan=2, pady=10)

        self.result_box = scrolledtext.ScrolledText(root, width=100, height=25)
        self.result_box.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    def perform_search(self):
        city = self.city_entry.get().strip()
        ci = self.checkin_entry.get().strip()
        co = self.checkout_entry.get().strip()
        adults = int(self.adults_var.get())

        self.result_box.delete(1.0, tk.END)
        self.result_box.insert(tk.END, f"Searching hotels in {city}...\n")

        hotels, summary = search_hotels(city, ci, co, adults)
        if not hotels:
            self.result_box.insert(tk.END, "No hotels found or no price data.\n")
            return

        # Print summary to console
        if summary:
            print("===== HOTEL PRICE SUMMARY =====")
            print("Unique price points:", summary["count"])
            print(f"Cheapest:         ${summary['cheapest']:.2f}")
            print(f"Average:          ${summary['average']:.2f}")
            print(f"Most Expensive:   ${summary['most_expensive']:.2f}")
            print("================================")

        # Display in GUI
        for h in sorted(hotels, key=lambda x: x["price"]):
            self.result_box.insert(tk.END,
                f"{h['hotel_name']} — ${h['price']:.2f} — via {h['provider']}\n"
            )

# ---------- RUN ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = HotelWhereXoteloGUI(root)
    root.mainloop()
