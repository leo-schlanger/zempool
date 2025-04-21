import statistics

# Fallback gerador de preços sintéticos
def get_historical_prices_stub(current_price):
    return [current_price * (0.95 + i * 0.001) for i in range(50)]

# Alias principal usado no generate.py (ainda usa stub)
def fetch_closing_prices(symbol_or_price):
    try:
        price = float(symbol_or_price)
        return get_historical_prices_stub(price)
    except Exception:
        return []

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
