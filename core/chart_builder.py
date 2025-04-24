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

def generate_range_chart(candles: list[dict], min_range: float, max_range: float, filename: str) -> str:
    dates = [datetime.fromtimestamp(int(c['t']) // 1000) for c in candles if c.get('c')]
    prices = [float(c['c']) for c in candles if c.get('c')]

    if not dates or not prices:
        return None

    plt.figure(figsize=(8, 4))
    plt.plot(dates, prices, linewidth=1.2, label="Close Price", color="black")
    plt.axhline(min_range, color="green", linestyle="--", linewidth=1, label="Range Min")
    plt.axhline(max_range, color="red", linestyle="--", linewidth=1, label="Range Max")
    # Faixa de range com fundo leve
    plt.axhspan(min_range, max_range, facecolor='purple', alpha=0.1)
    plt.plot(dates, min_range, max_range, color="yellow", alpha=0.15, label="Range Zone")

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())

    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(fontsize=8)
    plt.grid(False)
    plt.title("Price vs Suggested Range", fontsize=10)
    plt.tight_layout()
    plt.legend(fontsize=7, loc='upper left')

    if not filename.endswith(".png"):
        filename += ".png"
    plt.savefig(filename, dpi=150)
    plt.close()
    return filename


def validate_candles(candles):
    return isinstance(candles, list) and all('close' in c for c in candles)


import numpy as np

def get_range_coverage_ratio(prices, lower, upper):
    if not prices:
        return 1.0
    inside_range = [p for p in prices if lower <= p <= upper]
    return len(inside_range) / len(prices) if prices else 1.0