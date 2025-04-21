
import statistics

def fetch_closing_prices(symbol: str):
    return [1 + (i * 0.005) for i in range(40)]

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
