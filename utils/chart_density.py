import logging

import numpy as np
from statistics import quantiles

def get_price_range_by_density(closing_prices: list[float], percent_cover: float = 0.8) -> dict:
    if not closing_prices or len(closing_prices) < 10:
        return None

    prices = np.array(closing_prices)
    prices = prices[~np.isnan(prices)]  # remover NaN se houver

    lower_quantile = (1 - percent_cover) / 2
    upper_quantile = 1 - lower_quantile

    lower = np.quantile(prices, lower_quantile)
    upper = np.quantile(prices, upper_quantile)

    # Fallback: se lower == upper, aplica margem artificial de ±0.5%
    if lower == upper:
        logger = logging.getLogger("ZenPool")
        logger.warning("Density range lower == upper. Applying ±0.5% fallback margin.")
        lower *= 0.925
        upper *= 1.075

    return {
        "lower": round(float(lower), 4),
        "upper": round(float(upper), 4),
        "confidence": f"{int(percent_cover * 100)}% of daily closing prices"
    }



def get_range_coverage_ratio(prices, range_low, range_high):
    if not prices:
        return 0
    inside = [p for p in prices if range_low <= p <= range_high]
    return round(len(inside) / len(prices), 4)
