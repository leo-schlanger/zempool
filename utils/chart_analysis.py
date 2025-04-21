
import requests
import statistics

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

def suggest_price_range(prices):
    if not prices or len(prices) < 10:
        return None
    avg = statistics.mean(prices)
    stdev = statistics.stdev(prices)
    return {
        "lower": round(avg - 1.5 * stdev, 4),
        "upper": round(avg + 1.5 * stdev, 4),
        "confidence": "approx. 86% of price action"
    }
