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

        candles_filtered = candles[-(days * 6):]  # últimos 14 dias de candles 4h

        closes = []
        for c in candles_filtered:
            close = float(c.get("c", 0))
            if close > 0:
                closes.append(close)

        if not closes:
            logger.warning("[price_density] No valid closing prices found.")
            return None

        current_price = closes[-1]
        logger.info(f"[price_density] Current price: {current_price}")

        # Agrupar preços em buckets de ±0.5% do preço
        bucket_span = current_price * 0.005
        buckets = defaultdict(int)

        for close in closes:
            key = round(close // bucket_span * bucket_span, 4)
            buckets[key] += 1

        # Selecionar o bucket com maior densidade
        if not buckets:
            logger.warning("[price_density] No price buckets created.")
            return None

        sorted_buckets = sorted(buckets.items(), key=lambda x: x[1], reverse=True)

        best_bucket = sorted_buckets[0][0]

        lower = round(best_bucket - bucket_span, 4)
        upper = round(best_bucket + bucket_span, 4)

        # Garantir que o preço atual esteja dentro do range
        if not (lower <= current_price <= upper):
            logger.warning("⚠️ Fallback range applied ±0.5% around current price.")
            lower = round(current_price * 0.995, 4)
            upper = round(current_price * 1.005, 4)

        return (lower, upper)

    except Exception as e:
        logger.error(f"[ERROR] get_range_by_density_dexscreener failed: {e}")
        return None
