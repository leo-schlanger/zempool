
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

def get_support_resistance_zones(symbol: str, interval_days: int = 90, bucket_size: float = 0.25):
    try:
        response = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart",
            params={"vs_currency": "usd", "days": interval_days, "interval": "daily"},
            timeout=10
        )
        data = response.json()
        closes = [price[1] for price in data["prices"]]

        if len(closes) < 10:
            print("[Zone Calc] Not enough data.")
            return None

        # Bucketização com maior precisão
        bucketed = [round(price // bucket_size * bucket_size, 2) for price in closes]
        frequency = Counter(bucketed)

        # Ordena por frequência e depois por distância
        sorted_buckets = sorted(frequency.items(), key=lambda x: (-x[1], x[0]))

        # Garante dois buckets diferentes
        selected = []
        for bucket, count in sorted_buckets:
            if all(abs(bucket - b[0]) >= bucket_size for b in selected):
                selected.append((bucket, count))
            if len(selected) == 2:
                break

        if len(selected) < 2:
            print("[Zone Calc] Could not find two distinct support/resistance zones.")
            return None

        support = min(selected[0][0], selected[1][0])
        resistance = max(selected[0][0], selected[1][0])

        print(f"[Zone Calc] Selected zones: Support = {support}, Resistance = {resistance}")

        return {
            "support": support,
            "resistance": resistance,
            "bucket_size": bucket_size
        }

    except Exception as e:
        print(f"[Support/Resistance Error] {e}")
        return None

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.dates as mdates
from datetime import datetime
import os

def generate_range_chart(candles, range_min, range_max, chart_path):
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import datetime

    if not candles:
        return None

    dates = [datetime.datetime.fromtimestamp(int(candle["timestamp"]) / 1000) for candle in candles]
    closes = [float(candle["close"]) for candle in candles]

    plt.figure(figsize=(8, 4))
    min_range = range_min
    max_range = range_max
    plt.axhspan(min_range, max_range, facecolor='purple', alpha=0.1)
    plt.plot(dates, closes, label="Close Price", linewidth=1.5)

    plt.title("Price vs Suggested Range")
    plt.legend()
    plt.xticks(rotation=30)
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    return chart_path


def validate_candles(candles):
    return isinstance(candles, list) and all('close' in c for c in candles)

