
import requests
import statistics
from collections import Counter

def fetch_closing_prices(symbol: str):
    try:
        response = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart",
            params={"vs_currency": "usd", "days": 30, "interval": "daily"},
            timeout=10
        )
        data = response.json()
        prices = [p[1] for p in data["prices"]]
        return prices
    except Exception as e:
        print(f"[Chart Fetch Error] {e}")
        return []

def get_support_resistance_zones(symbol: str, interval_days: int = 90, bucket_size: float = 1.0):
    try:
        response = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart",
            params={"vs_currency": "usd", "days": interval_days, "interval": "daily"},
            timeout=10
        )
        data = response.json()
        closes = [price[1] for price in data["prices"]]

        if len(closes) < 10:
            return None

        bucketed = [round(price // bucket_size * bucket_size, 2) for price in closes]
        frequency = Counter(bucketed)
        top_two = frequency.most_common(2)
        if len(top_two) < 2:
            return None

        support = min(top_two[0][0], top_two[1][0])
        resistance = max(top_two[0][0], top_two[1][0])

        return {
            "support": support,
            "resistance": resistance,
            "bucket_size": bucket_size,
            "count_data": frequency
        }
    except Exception as e:
        print(f"[Support/Resistance Error] {e}")
        return None
