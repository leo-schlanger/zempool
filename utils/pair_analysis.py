
import requests
from collections import Counter

def get_support_resistance_from_pair(pair_slug: str, interval: str = "1d", limit: int = 90, bucket_size: float = 0.005):
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/{pair_slug}/candles?interval={interval}&limit={limit}"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"[DexScreener] Error fetching candles for {pair_slug}")
            return None

        candles = response.json().get("candles", [])
        closes = [float(candle["close"]) for candle in candles if "close" in candle]

        if len(closes) < 10:
            print("[Zone Calc] Not enough candle data.")
            return None

        # Bucketizar com precisão ajustada ao range do par (0.5% de média do par)
        bucketed = [round(price // bucket_size * bucket_size, 6) for price in closes]
        frequency = Counter(bucketed)

        sorted_buckets = sorted(frequency.items(), key=lambda x: (-x[1], x[0]))

        # Garantir dois buckets diferentes
        selected = []
        for bucket, count in sorted_buckets:
            if all(abs(bucket - b[0]) >= bucket_size for b in selected):
                selected.append((bucket, count))
            if len(selected) == 2:
                break

        if len(selected) < 2:
            print("[Zone Calc] Could not find distinct support/resistance zones.")
            return None

        support = min(selected[0][0], selected[1][0])
        resistance = max(selected[0][0], selected[1][0])

        print(f"[DEX PAIR RANGE] {pair_slug}: Support = {support}, Resistance = {resistance}")

        return {
            "support": support,
            "resistance": resistance,
            "bucket_size": bucket_size
        }

    except Exception as e:
        print(f"[DexScreener Error] {e}")
        return None
