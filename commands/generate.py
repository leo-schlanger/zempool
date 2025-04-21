import discord
from discord import app_commands
from config.supported_networks import SUPPORTED_NETWORKS
from utils.fetch_pool import fetch_pool_data
from utils.simulate_earnings import simulate_apr_apy, format_small_number
from utils.chart_analysis import fetch_closing_prices
from statistics import quantiles
from external_aprs.unified_apr import get_best_real_apr
import logging

logger = logging.getLogger("ZenPool")

SYMBOL_MAP = {
    "sol": "solana",
    "eth": "ethereum",
    "btc": "bitcoin",
    "usdc": "usd-coin",
    "usdt": "tether",
    "avax": "avalanche-2",
    "op": "optimism",
    "arb": "arbitrum",
    "matic": "polygon",
    "link": "chainlink"
}

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

            real_apr_info = get_best_real_apr(pair, network)
            apr_value = real_apr_info["apr"] if real_apr_info else info.get("apr")
            if not apr_value:
                await interaction.followup.send("❌ Could not retrieve APR data.")
                return

            earnings = simulate_apr_apy(apr_value, info["volume_usd"], info["liquidity_usd"])
            if earnings is None:
                await interaction.followup.send("❌ Could not calculate APR.")
                return

            base_token = info["pair"].split("/")[0].lower()
            symbol = SYMBOL_MAP.get(base_token, base_token)
            prices = fetch_closing_prices(symbol)

            if len(prices) >= 10:
                price_range_quantiles = quantiles(prices, n=100)
                price_range = {
                    "lower": round(price_range_quantiles[10], 4),
                    "upper": round(price_range_quantiles[90], 4),
                    "confidence": "approx. 80% of price action (quantile based)"
                }
            else:
                price_range = {
                    "lower": info["price_usd"],
                    "upper": info["price_usd"],
                    "confidence": "⚠️ Not enough data for range"
                }

            apr_daily = round(apr_value / 365, 4)
            apr_weekly = round(apr_value / 52, 4)

            msg = f"""**🧘 ZenPool Analysis Complete!**\n
**Pair:** {info['pair']}
**Network:** {info['network']}
**DEX:** {info['dex']}
**Price:** `$ {format_small_number(info['price_usd'])}`
**Volume:** `$ {info['volume_usd']:,.2f}`
**Liquidity:** `$ {info['liquidity_usd']:,.2f}`
**APR:** {apr_value}%\n
**APR Estimates:**\n• Daily: {apr_daily}%\n• Weekly: {apr_weekly}%\n• Yearly: {apr_value}%\n
**Range:** `$ {format_small_number(price_range['lower'])}` - `$ {format_small_number(price_range['upper'])}`\n
*Note: Gas and IL not included.*"""

            await interaction.followup.send(msg)
        except Exception as e:
            logger.error(f"ZenPool Error: {e}")
            await interaction.followup.send("❌ Unexpected error occurred.")
