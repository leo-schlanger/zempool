
import requests
import logging

logger = logging.getLogger("ZenPool")

def fetch_pool_data(network: str, pair_address: str):
    try:
        url = f"https://api.dexscreener.com/experimental/pair/{network}/{pair_address}"
        logger.info(f"[fetch_pool_data] Requesting: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Suporte tanto para 'pair' quanto 'pairs[0]'
        pair = data.get("pair") or data.get("pairs", [{}])[0]

        if not pair or "baseToken" not in pair or "quoteToken" not in pair:
            logger.warning("[fetch_pool_data] Invalid response structure or missing token info")
            return "❌ Could not fetch data for this pair."

        # Logging de dados brutos
        logger.debug(f"[fetch_pool_data] Raw: volume={pair.get('volume')}, liquidity={pair.get('liquidity')}")

        return {
            "pair": f"{pair['baseToken']['symbol']}/{pair['quoteToken']['symbol']}",
            "network": pair.get("chainId", network),
            "dex": pair.get("dexId", "unknown"),
            "price_usd": float(pair.get("priceUsd", 0)),
            "volume_usd": float(pair.get("volume", {}).get("h24", 0)),
            "liquidity_usd": float(pair.get("liquidity", {}).get("usd", 0))
        }

    except Exception as e:
        logger.error(f"[fetch_pool_data] Error: {e}")
        return "❌ Could not fetch data for this pair."
