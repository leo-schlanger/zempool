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
from external_aprs.unified_apr import get_best_real_apr
from ui.reanalyze_view import ReanalyzeView

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
        symbol = info["pair"]
        real_apr_info = get_best_real_apr(symbol, network)
        real_apr = real_apr_info["apr"] if real_apr_info and real_apr_info.get("apr", 0) > 0 else None

        logger.debug(f"[APR] volume={info['volume_usd']} | liquidity={info['liquidity_usd']} | fee={fee_rate}")
        apr_value = (
            real_apr if real_apr
            else round((info["volume_usd"] / info["liquidity_usd"]) * fee_rate * 365 * 100, 2)
            if info["volume_usd"] > 0 and info["liquidity_usd"] > 0 else 0
        )
        logger.info(f"[APR] {'Real' if real_apr else 'Estimated'} APR: {apr_value}%")

        earnings = simulate_apr_apy(apr_value, info["volume_usd"], info["liquidity_usd"])
        if earnings is None:
            await interaction.followup.send("❌ Could not calculate APR.")
            return

        closes = fetch_closing_prices(info["pair"].split("/")[0].lower())
        range_auto = get_range_by_density_dexscreener(network, pair)
        logger.info(f"[RANGE] Auto result: {range_auto}")

        if range_auto:
            price_now = info["price_usd"]
            range_width = range_auto[1] - range_auto[0]
            if (range_width / price_now) < 0.02:
                logger.warning("[RANGE] Too narrow (<2%) - fallback")
                range_auto = None

        if range_auto:
            price_range = {
                "lower": range_auto[0],
                "upper": range_auto[1],
                "confidence": "Dense range based on 90d (4h candles)"
            }
        else:
            price = info["price_usd"]
            price_range = {
                "lower": round(price * 0.995, 4),
                "upper": round(price * 1.005, 4),
                "confidence": "Fallback ±0.5% range applied"
            }

        # Buscar candles DexScreener (ou lidar com ausência)
        try:
            url = f"https://api.dexscreener.com/experimental/pair/{network}/{pair}/chart?interval=4h"
            response = requests.get(url, timeout=10)
            candles = response.json().get("pairs", [{}])[0].get("chart", [])
            if not candles or not isinstance(candles, list):
                raise ValueError("DexScreener returned no valid candles")
        except Exception as err:
            logger.warning(f"[CHART] DexScreener failed: {err}")
            candles = []

        if candles:
            chart_path = f"range_{pair.replace('/', '_')}.png"
            chart_result = generate_range_chart(candles, price_range['lower'], price_range['upper'], chart_path)
        else:
            chart_result = None

        coverage = get_range_coverage_ratio(closes, price_range["lower"], price_range["upper"])
        apr_value = round(apr_value * coverage, 2)
        logger.info(f"[COVERAGE] {coverage*100:.2f}% → APR: {apr_value}%")

        apr_daily = round(apr_value / 365, 4)
        apr_weekly = round(apr_value / 52, 4)
        capital = 1000
        earn_day = round((apr_value / 100) / 365 * capital, 2)
        earn_week = round((apr_value / 100) / 52 * capital, 2)
        earn_year = round((apr_value / 100) * capital, 2)

        msg = f"""**🧘 ZenPool Analysis Complete!**

**Pair:** {info['pair']}
**Network:** {info['network']}
**DEX:** {info['dex']} (Fee: {round(fee_rate * 100, 2)}%)
**Price:** `$ {format_small_number(info['price_usd'])}`
**Volume:** `$ {info['volume_usd']:,.2f}`
**Liquidity:** `$ {info['liquidity_usd']:,.2f}`
**APR:** {apr_value}% (adjusted for range coverage)

**APR Estimates:**
• Daily: {apr_daily}%
• Weekly: {apr_weekly}%
• Yearly: {apr_value}%

**Range:** `$ {format_small_number(price_range['lower'])}` - `$ {format_small_number(price_range['upper'])}`\n*{price_range.get("confidence", "")}*
*Note: Gas and IL not included.*

**Earnings Estimation (for $1000 in pool):**
• Daily: `$ {earn_day}`
• Weekly: `$ {earn_week}`
• Yearly: `$ {earn_year}`
"""

        await interaction.followup.send(content=msg, file=discord.File(chart_result) if chart_result else None, view=ReanalyzeView(interaction.client, network, pair))

    except Exception as e:
        logger.error(f"[analyze_pair] Error: {e}")
        await interaction.followup.send("❌ Unexpected error occurred.")
