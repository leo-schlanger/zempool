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

        if not data or "pair" not in data or not data["pair"]:
            logger.warning(f"[fetch_pool_data] No 'pair' found in response for {network}/{pair_address}")
            return "❌ Could not fetch data for this pair."

        pair = data["pair"]

        price_usd = float(pair.get("priceUsd", 0))
        volume_24h = float(pair.get("volume", {}).get("h24", 0))
        liquidity_usd = float(pair.get("liquidity", {}).get("usd", 1))  # avoid division by zero

        estimated_apr = round((volume_24h * 0.003 / liquidity_usd) * 365 * 100, 2)

        result = {
            "pair": f"{pair['baseToken']['symbol']}/{pair['quoteToken']['symbol']}",
            "network": pair["chainId"],
            "dex": pair["dexId"],
            "price_usd": price_usd,
            "volume_usd": volume_24h,
            "liquidity_usd": liquidity_usd,
            "apr": estimated_apr
        }

        logger.info(f"[fetch_pool_data] Successfully fetched: {result}")
        return result

    except requests.exceptions.Timeout:
        logger.error(f"[fetch_pool_data] Timeout when requesting {network}/{pair_address}")
        return "❌ Request timed out. Try again later."

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"[fetch_pool_data] HTTP error: {http_err}")
        return f"❌ HTTP error occurred: {http_err}"

    except Exception as e:
        logger.exception(f"[fetch_pool_data] Unexpected error fetching data: {e}")
        return "❌ Could not fetch data for this pair."
