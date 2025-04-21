import requests

def fetch_pool_data(network: str, pair_address: str):
    try:
        api_url = f"https://api.dexscreener.com/latest/dex/pairs/{network}/{pair_address}"
        response = requests.get(api_url, timeout=10)

        if response.status_code != 200:
            return f"❌ Error accessing API: {response.status_code}"

        pair_data = response.json().get("data")
        if not pair_data:
            return "❌ Could not fetch data for this pair."

        base_token = pair_data.get("baseToken", {})
        quote_token = pair_data.get("quoteToken", {})
        token0 = pair_data.get("token0", {})
        token1 = pair_data.get("token1", {})

        price_native = float(pair_data.get("priceNative", 0))
        if token0 and base_token.get("address", "").lower() != token0.get("address", "").lower():
            price_native = 1 / price_native if price_native != 0 else 0

        return {
            "pair": f"{base_token.get('symbol', 'BASE')}/{quote_token.get('symbol', 'QUOTE')}",
            "network": pair_data.get("chainId", network),
            "dex": pair_data.get("dexId", "unknown"),
            "price_usd": price_native,
            "volume_usd": pair_data.get("volume", {}).get("h24", 0),
            "liquidity_usd": pair_data.get("liquidity", {}).get("usd", 0),
            "apr": pair_data.get("farmed", {}).get("apr", "N/A"),
        }

    except Exception as e:
        return f"❌ An error occurred: {str(e)}"