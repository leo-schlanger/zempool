import requests
import logging
from collections import defaultdict

logger = logging.getLogger("ZenPool")

def get_range_by_density_dexscreener(network: str, pair_address: str, interval: str = "4h", days: int = 14) -> tuple | None:
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/{pair_address}/chart?interval={interval}"
        logger.info(f"[price_density] Fetching candles from: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        candles = data.get("pairs", [{}])[0].get("chart", [])
        if not candles or len(candles) < 10:
            logger.warning("[price_density] Not enough candle data.")
            return None

        closes = [float(c["c"]) for c in candles if float(c.get("c", 0)) > 0]
        if not closes:
            logger.warning("[price_density] No valid closing prices found.")
            return None

        current_price = closes[-1]
        logger.info(f"[price_density] Current price: {current_price}")

        bucket_span = current_price * 0.005
        buckets = defaultdict(int)

        for close in closes:
            key = round(close // bucket_span * bucket_span, 4)
            buckets[key] += 1

        if not buckets:
            logger.warning("[price_density] No price buckets created.")
            return None

        best_bucket = max(buckets, key=buckets.get)
        lower = round(best_bucket - bucket_span, 4)
        upper = round(best_bucket + bucket_span, 4)

        if not (lower <= current_price <= upper):
            logger.warning("⚠️ Fallback range applied ±0.5% around current price.")
            lower = round(current_price * 0.995, 4)
            upper = round(current_price * 1.005, 4)

        return (lower, upper)

    except Exception as e:
        logger.error(f"[ERROR] get_range_by_density_dexscreener failed: {e}")
        return None
