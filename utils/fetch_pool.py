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

        base_symbol = base_token.get("symbol", "BASE")
        quote_symbol = quote_token.get("symbol", "QUOTE")

        # Preço do par no formato base/quote (ex: SOL/ETH = quantos ETH por 1 SOL)
        price_usd = float(data["priceUsd"])
        price_native = float(data["priceNative"])
        price_quote = price_usd if quote_symbol.upper() in ["USD", "USDC", "USDT"] else price_native

        return {
            "pair": f"{base_symbol}/{quote_symbol}",
            "network": data.get("chainId", network),
            "dex": data.get("dexId", "unknown"),
            "price_usd": price_quote,
            "volume_usd": data.get("volume", {}).get("h24", 0),
            "liquidity_usd": data.get("liquidity", {}).get("usd", 0),
            "apr": data.get("farmed", {}).get("apr", "N/A"),
        }

    except Exception as e:
        return f"❌ An error occurred: {str(e)}"