import discord
from discord import app_commands
from config.supported_networks import SUPPORTED_NETWORKS
from utils.fetch_pool import fetch_pool_data
from utils.simulate_earnings import simulate_apr_apy, format_small_number
from utils.chart_analysis import generate_range_chart, fetch_closing_prices
from utils.price_density import get_range_by_density_dexscreener
from external_aprs.unified_apr import get_best_real_apr
from utils.chart_density import get_range_coverage_ratio
import logging
import json
import os
import requests

logger = logging.getLogger("ZenPool")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("zenpool_debug.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class GenerateCommand(app_commands.Command):
    def __init__(self):
        super().__init__(
            name="generate",
            description="Analyze a pair and simulate LP returns",
            callback=self.callback
        )
        self.autocomplete("network")(self.network_autocomplete)

    async def network_autocomplete(self, interaction: discord.Interaction, current: str):
        try:
            return [app_commands.Choice(name=net, value=net)
                    for net in SUPPORTED_NETWORKS if current.lower() in net.lower()][:25]
        except Exception as e:
            logger.error(f"[autocomplete] Error: {e}")
            return []

    async def callback(self, interaction: discord.Interaction, network: str, pair: str):
        try:
            await interaction.response.defer(thinking=True)
            logger.info(f"Running analysis for {network} / {pair}")

            info = fetch_pool_data(network, pair)
            if isinstance(info, str):
                await interaction.followup.send(info)
                return

            # Load DEX fees from JSON
            with open(os.path.join("config", "dex_fees.json")) as f:
                dex_fee_rates = json.load(f)

            fee_rate = dex_fee_rates.get(info["dex"].lower(), 0.003)
            logger.info(f"Using fee rate for DEX {info['dex']}: {fee_rate}")

            symbol = info["pair"]
            real_apr_info = get_best_real_apr(symbol, network)

            real_apr = real_apr_info["apr"] if real_apr_info and real_apr_info.get("apr", 0) > 0 else None
            apr_value = real_apr if real_apr else round(
                (info["volume_usd"] / info["liquidity_usd"]) * fee_rate * 365 * 100, 2)

            if not apr_value:
                await interaction.followup.send("❌ Could not retrieve APR data.")
                return

            earnings = simulate_apr_apy(apr_value, info["volume_usd"], info["liquidity_usd"])
            if earnings is None:
                await interaction.followup.send("❌ Could not calculate APR.")
                return

            closes = fetch_closing_prices(info["pair"].split("/")[0].lower())

            # Tentar range automático
            range_auto = get_range_by_density_dexscreener(network, pair)
            if range_auto:
                price_now = info["price_usd"]
                range_width = range_auto[1] - range_auto[0]
                range_ratio = range_width / price_now
                if range_ratio < 0.02:
                    logger.warning("[range] Range width too narrow, falling back to manual range.")
                    range_auto = None

            # Aplicar range final
            if range_auto:
                price_range = {
                    "lower": range_auto[0],
                    "upper": range_auto[1],
                    "confidence": "Dense range based on 90d (4h candles)"
                }
                # Gerar gráfico
                url_candle = f"https://api.dexscreener.com/latest/dex/pairs/{network}/{pair}/chart?interval=4h"
                response = requests.get(url_candle, timeout=10)
                candles = response.json().get("pairs", [{}])[0].get("chart", [])
                chart_path = f"range_{pair.replace('/', '_')}.png"
                chart_result = generate_range_chart(candles, price_range['lower'], price_range['upper'], chart_path)
            else:
                price = info["price_usd"]
                price_range = {
                    "lower": round(price * 0.995, 4),
                    "upper": round(price * 1.005, 4),
                    "confidence": "Fallback ±0.5% range applied"
                }
                chart_result = None

            # Ajustar APR pela cobertura do range
            coverage = get_range_coverage_ratio(closes, price_range["lower"], price_range["upper"])
            apr_value = round(apr_value * coverage, 2)
            logger.info(f"Range coverage: {coverage*100:.2f}%")

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

            if chart_result:
                await interaction.followup.send(content=msg, file=discord.File(chart_result))
            else:
                await interaction.followup.send(content=msg)

        except Exception as e:
            logger.error(f"ZenPool Error: {e}")
            await interaction.followup.send("❌ Unexpected error occurred.")
