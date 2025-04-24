import requests
import logging
from collections import defaultdict

logger = logging.getLogger("ZenPool")

def get_range_by_density_dexscreener(network: str, pair_address: str, interval: str = "4h", days: int = 14) -> tuple | None:
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

        candles_filtered = candles[-(days * 6):]  # 6 candles por dia (4h)

        buckets = defaultdict(int)
        prices = []

        for c in candles_filtered:
            close = float(c.get("c", 0))
            if close == 0:
                continue
            prices.append(close)
            bucket_key = round(close, 4)
            buckets[bucket_key] += 1

        if not buckets:
            logger.warning("[price_density] Bucket calculation failed.")
            return None

        # Ordenar por densidade
        sorted_buckets = sorted(buckets.items(), key=lambda x: x[1], reverse=True)

        # Pegar os N mais densos e garantir que o preço atual esteja dentro
        top_n = 20
        top_prices = [b[0] for b in sorted_buckets[:top_n]]

        # Calcular range incluindo o preço atual
        current_price = prices[-1]
        logger.info(f"[price_density] Current price: {current_price}")
        surrounding = [p for p in top_prices if abs(p - current_price) / current_price <= 0.2]

        if not surrounding:
            logger.warning("[price_density] No dense buckets near current price. Returning fallback.")
            return None

        range_lower = round(min(surrounding), 4)
        range_upper = round(max(surrounding), 4)

        return (range_lower, range_upper)

    except Exception as e:
        logger.error(f"[ERROR] get_range_by_density_dexscreener failed: {e}")
        return None
