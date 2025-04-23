import os
import json
import requests
import logging
import discord
from utils.fetch_pool import fetch_pool_data
from utils.simulate_earnings import simulate_apr_apy, format_small_number
from utils.chart_analysis import generate_range_chart, fetch_closing_prices
from utils.price_density import get_range_by_density_dexscreener
from utils.chart_density import get_range_coverage_ratio
from utils.response import send_analysis_result

logger = logging.getLogger("ZenPool")

async def analyze_pair(interaction: discord.Interaction, network: str, pair: str):
    try:
        info = fetch_pool_data(network, pair)
        if isinstance(info, str):
            await interaction.followup.send(info)
            return

        with open(os.path.join("config", "dex_fees.json")) as f:
            dex_fee_rates = json.load(f)
        fee_rate = dex_fee_rates.get(info["dex"].lower(), 0.003)

        logger.info(f"[FEE] {info['dex']} = {fee_rate}")

        real_apr = None
        logger.debug(f"[APR] volume={info['volume_usd']} | liquidity={info['liquidity_usd']} | fee={fee_rate}")
        apr_value = (
            real_apr if real_apr
            else round((info["volume_usd"] / info["liquidity_usd"]) * fee_rate * 365 * 100, 2)
            if info["volume_usd"] > 0 and info["liquidity_usd"] > 0 else 0
        )
        logger.info(f"[APR] Estimated APR: {apr_value}%")

        closes = fetch_closing_prices(info["pair"].split("/")[0].lower())
        range_auto = get_range_by_density_dexscreener(network, pair)
        logger.info(f"[RANGE] Auto result: {range_auto}")

        if range_auto:
            price_now = info["price_usd"]
            range_width = range_auto[1] - range_auto[0]
            if (range_width / price_now) < 0.02:
                logger.warning("[RANGE] Too narrow (<2%) - fallback")
                range_auto = None

        price_range = {
            "lower": range_auto[0],
            "upper": range_auto[1],
            "confidence": "Dense range based on 90d (4h candles)"
        } if range_auto else {
            "lower": round(info["price_usd"] * 0.995, 4),
            "upper": round(info["price_usd"] * 1.005, 4),
            "confidence": "Fallback ±0.5% range applied"
        }

        try:
            url = f"https://api.dexscreener.com/experimental/pair/{network}/{pair}/chart?interval=4h"
            response = requests.get(url, timeout=10)
            candles = response.json().get("pairs", [{}])[0].get("chart", [])
            if not candles or not isinstance(candles, list):
                raise ValueError("DexScreener returned no valid candles")
        except Exception as err:
            logger.warning(f"[CHART] DexScreener failed: {err}")
            candles = []

        coverage = get_range_coverage_ratio(closes, price_range["lower"], price_range["upper"])
        apr_value = round(apr_value * coverage, 2)
        logger.info(f"[COVERAGE] {coverage*100:.2f}% → APR: {apr_value}%")

        await send_analysis_result(
            interaction=interaction,
            info={**info, "fee_rate": fee_rate},
            network=network,
            pair=pair,
            apr_value=apr_value,
            price_range=price_range,
            closes=closes,
            candles=candles
        )
    except Exception as e:
        logger.error(f"[analyze_pair] Error: {e}")
        await interaction.followup.send("❌ Unexpected error occurred.")
