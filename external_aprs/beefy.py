import requests

BEEFY_API = "https://api.beefy.finance/vaults"

def fetch_beefy_aprs():
    try:
        response = requests.get(BEEFY_API, timeout=10))
        if response.status_code != 200:
            return []

        vaults = response.json()
        results = []

        for vault in vaults:
            if vault.get("status") != "active":
                continue
            apr = vault.get("apy", {}).get("totalApy")
            if apr is None:
                continue

            results.append({
                "id": vault.get("id"),
                "name": vault.get("name"),
                "platform": vault.get("platformId"),
                "network": vault.get("network"),
                "asset": vault.get("asset"),
                "underlying_tokens": vault.get("tokenAddress"),
                "apy": round(float(apr) * 100, 2),  # convert to %
                "url": f"https://app.beefy.finance/vault/{vault.get('id')}"
            })

        return results
    except Exception as e:
        return []

def match_beefy_apr(pair_address: str, network: str):
    network = network.lower().replace(" ", "")
    vaults = fetch_beefy_aprs()

    matches = [v for v in vaults if v["network"] == network and v["underlying_tokens"].lower() == pair_address.lower()]
    return matches