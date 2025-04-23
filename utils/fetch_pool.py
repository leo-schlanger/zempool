
import requests
import logging

logger = logging.getLogger("ZenPool")

def fetch_pool_data(network: str, pair_address: str):
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/{network}/{pair_address}"
        logger.info(f"[fetch_pool_data] Requesting: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("pair"):
            return "❌ Could not fetch data for this pair."

        pair = data["pair"]
        return {
            "pair": f"{pair['baseToken']['symbol']}/{pair['quoteToken']['symbol']}",
            "network": pair["chainId"],
            "dex": pair["dexId"],
            "price_usd": float(pair["priceUsd"]),
            "volume_usd": float(pair["volume"]["h24"]),
            "liquidity_usd": float(pair["liquidity"]["usd"]),
            "apr": round((float(pair["volume"]["h24"]) * 0.003 / float(pair["liquidity"]["usd"])) * 365 * 100, 2)
        }
    except Exception as e:
        logger.error(f"[fetch_pool_data] Error: {e}")
        return "❌ Could not fetch data for this pair."
