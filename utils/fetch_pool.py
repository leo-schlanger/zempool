import requests

def fetch_pool_data(url):
    try:
        parts = url.rstrip("/").split("/")
        network, pair_address = parts[-2], parts[-1]

        api_url = f"https://api.dexscreener.com/latest/dex/pairs/{network}/{pair_address}"
        response = requests.get(api_url)

        if response.status_code != 200:
            return "❌ Error accessing API: 404"

        data = response.json().get("pair")
        if not data:
            return "❌ Could not fetch data for this pair."

        base_token = data["baseToken"]
        quote_token = data["quoteToken"]
        token0 = data.get("token0")
        token1 = data.get("token1")

        base_symbol = base_token.get("symbol", "BASE")
        quote_symbol = quote_token.get("symbol", "QUOTE")

        price_native = float(data["priceNative"])
        # Corrigir inversão: se base != token0, inverter
        if base_token["address"].lower() != token0["address"].lower():
            price_native = 1 / price_native

        return {
            "pair": f"{base_symbol}/{quote_symbol}",
            "network": data.get("chainId", network),
            "dex": data.get("dexId", "unknown"),
            "price_usd": price_native,
            "volume_usd": data.get("volume", {}).get("h24", 0),
            "liquidity_usd": data.get("liquidity", {}).get("usd", 0),
            "apr": data.get("farmed", {}).get("apr", "N/A"),
        }

    except Exception as e:
        return f"❌ An error occurred: {str(e)}"