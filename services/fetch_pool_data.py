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

        pair = data.get("pair") or data.get("pairs", [{}])[0]

        if not pair or not pair.get("baseToken") or not pair.get("quoteToken"):
            logger.warning("[fetch_pool_data] Invalid response structure or missing token info")
            return "❌ Could not fetch data for this pair."

        price_usd = float(pair.get("priceUsd", 0))
        volume_usd = float(pair.get("volume", {}).get("h24", 0))
        liquidity_usd = float(pair.get("liquidity", {}).get("usd", 0))
        fee_rate = float(pair.get("fee", 0.003))

        if volume_usd == 0 or liquidity_usd == 0 or fee_rate == 0:
            return "❌ APR cannot be estimated: No fee, volume or liquidity"

        return {
            "pair": f"{pair['baseToken']['symbol']}/{pair['quoteToken']['symbol']}",
            "network": pair.get("chainId", network),
            "dex": pair.get("dexId", "unknown"),
            "price_usd": price_usd,
            "volume_usd": volume_usd,
            "liquidity_usd": liquidity_usd,
            "fee_rate": fee_rate
        }

    except Exception as e:
        logger.error(f"[fetch_pool_data] Error: {e}")
        return "❌ Could not fetch data for this pair."
