from external_aprs.beefy import match_beefy_apr

def get_best_real_apr(pair_address: str, network: str):
    network = network.lower()

    if network in ["ethereum", "bsc", "polygon", "arbitrum", "optimism", "fantom", "avax", "base", "cronos"]:
        beefy = match_beefy_apr(pair_address, network)
        if beefy:
            return {
                "source": "Beefy",
                "apr": beefy[0]["apy"],
                "url": beefy[0]["url"]
            }

    return None