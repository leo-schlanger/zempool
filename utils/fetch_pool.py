import requests
import re

def fetch_pool_data(full_url):
    """
    Given a Dexscreener URL in the format:
    https://dexscreener.com/{network}/{pairAddress}

    This function uses the official API:
    https://api.dexscreener.com/latest/dex/pairs/{network}/{pairAddress}
    """
    try:
        match = re.search(r'dexscreener\.com/([^/]+)/([0x\w]+)', full_url)
        if not match:
            return "Invalid URL format. Expected: https://dexscreener.com/{network}/{pairAddress}"

        network, pair_address = match.group(1), match.group(2)
        api_url = f"https://api.dexscreener.com/latest/dex/pairs/{network}/{pair_address}"

        response = requests.get(api_url)
        if response.status_code != 200:
            return f"Error accessing API: {response.status_code}"

        data = response.json()
        pair_data = data.get("pair")

        if not pair_data:
            return "Pair not found or unavailable on the specified network."

        return {
            "network": pair_data.get("chainId"),
            "dex": pair_data.get("dexId"),
            "pair": f"{pair_data['baseToken']['symbol']}/{pair_data['quoteToken']['symbol']}",
            "price_usd": pair_data.get("priceUsd"),
            "volume_usd": pair_data.get("volume", {}).get("h24"),
            "liquidity_usd": pair_data.get("liquidity", {}).get("usd"),
            "apr": pair_data.get("farmed", {}).get("apr", "N/A"),
            "token_address": pair_address
        }

    except Exception as e:
        return f"Unexpected error: {str(e)}"