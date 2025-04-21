import requests

def fetch_pool_data(url):
    try:
        parts = url.rstrip("/").split("/")
        network, pair_address = parts[-2], parts[-1]

        api_url = f"https://api.dexscreener.com/latest/dex/pairs/{network}/{pair_address}"
        response = requests.get(api_url)

        if response.status_code != 200:
            return f"❌ Error accessing API: {response.status_code} — {response.reason}"

        data = response.json().get("pair")
        if not data:
            return "❌ Could not fetch data for this pair."

        base_token = data.get("baseToken")
        quote_token = data.get("quoteToken")
        token0 = data.get("token0")

        if not base_token or not quote_token or not token0 or "priceNative" not in data:
            return "❌ Invalid pool data received from API."

        base_symbol = base_token.get("symbol", "BASE")
        quote_symbol = quote_token.get("symbol", "QUOTE")

        price_native = float(data["priceNative"])
        if base_token["address"].lower() != token0["address"].lower():
            price_native = 1 / price_native

        apr_value = data.get("farmed", {}).get("apr")
        apr = apr_value if apr_value not in [None, "N/A"] else "Estimated"

        return {
            "pair": f"{base_symbol}/{quote_symbol}",
            "network": data.get("chainId", network),
            "dex": data.get("dexId", "unknown"),
            "price_usd": price_native,
            "volume_usd": data.get("volume", {}).get("h24", 0),
            "liquidity_usd": data.get("liquidity", {}).get("usd", 0),
            "apr": apr
        }

    except Exception as e:
        return f"❌ An error occurred: {str(e)}"