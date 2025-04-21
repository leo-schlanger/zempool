
import statistics

def get_historical_prices_stub(current_price):
    return [current_price * (0.95 + i * 0.001) for i in range(50)]

def suggest_price_range(prices):
    if not prices or len(prices) < 10:
        return None

    avg = statistics.mean(prices)
    stdev = statistics.stdev(prices)

    lower_bound = round(avg - 1.5 * stdev, 4)
    upper_bound = round(avg + 1.5 * stdev, 4)

    return {
        "lower": lower_bound,
        "upper": upper_bound,
        "confidence": "approx. 86% of price action"
    }
