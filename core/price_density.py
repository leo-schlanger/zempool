import requests
import logging
from collections import defaultdict

logger = logging.getLogger("ZenPool")

def get_range_by_density_dexscreener(network: str, pair_address: str, interval: str = "4h", days: int = 90) -> tuple | None:
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/{network}/{pair_address}/chart?interval={interval}"
        logger.info(f"[price_density] Fetching candles from: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        candles = data.get("pairs", [{}])[0].get("chart", [])
        if not candles or len(candles) < 10:
            logger.warning("[price_density] Not enough candle data.")
            return None

        # Converter e filtrar os últimos `days` dias de candles
        candles_filtered = candles[-(days * 6):]  # 6 candles de 4h por dia

        bucket_size_pct = 0.01  # 1% buckets
        buckets = defaultdict(int)

        for c in candles_filtered:
            high = float(c.get("h", 0))
            low = float(c.get("l", 0))
            if high == 0 or low == 0:
                continue
            avg_price = (high + low) / 2
            bucket_key = round(avg_price, 4)
            buckets[bucket_key] += 1

        if not buckets:
            logger.warning("[price_density] Bucket calculation failed.")
            return None

        # Encontrar os buckets mais densos
        sorted_buckets = sorted(buckets.items(), key=lambda x: x[1], reverse=True)
        top = sorted_buckets[:5]
        prices = [p[0] for p in top]
        min_range = round(min(prices), 4)
        max_range = round(max(prices), 4)

        logger.info(f"[price_density] Range found: {min_range} - {max_range}")
        return (min_range, max_range)

    except Exception as e:
        logger.error(f"[price_density] Error: {e}")
        return None
