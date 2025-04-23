
import requests
import logging

logger = logging.getLogger("ZenPool")

def fetch_candles_fallback_coingecko(token_id: str, days: int = 90) -> list:
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart?vs_currency=usd&days={days}&interval=daily"
        logger.info(f"[FALLBACK] Fetching candles from CoinGecko: {url}")
        response = requests.get(url, timeout=10)
        data = response.json()
        prices = data.get("prices", [])

        candles = [{"c": str(round(price[1], 6)), "t": str(int(price[0]))} for price in prices]
        return candles

    except Exception as e:
        logger.warning(f"[FALLBACK] CoinGecko candle fetch failed: {e}")
        return []
