
import requests
from collections import Counter

def fetch_closing_prices(symbol: str):
    try:
        response = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart",
            params={"vs_currency": "usd", "days": 30, "interval": "daily"},
            timeout=10
        )
        data = response.json()
        return [p[1] for p in data["prices"]]
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

        # Agrupar fechamentos em buckets
        bucketed = [round(price // bucket_size * bucket_size, 2) for price in closes]
        frequency = Counter(bucketed)

        # Garantir que temos pelo menos dois buckets diferentes
        distinct_buckets = sorted(frequency.items(), key=lambda x: (-x[1], x[0]))
        distinct = []
        for bucket, count in distinct_buckets:
            if all(abs(bucket - b[0]) >= 0.5 for b in distinct):
                distinct.append((bucket, count))
            if len(distinct) == 2:
                break

        if len(distinct) < 2:
            return None

        support = min(distinct[0][0], distinct[1][0])
        resistance = max(distinct[0][0], distinct[1][0])

        return {
            "support": support,
            "resistance": resistance,
            "bucket_size": bucket_size
        }

    except Exception as e:
        print(f"[Support/Resistance Error] {e}")
        return None
