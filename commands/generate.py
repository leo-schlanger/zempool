# coding: utf-8
import discord
from discord import app_commands
from config.supported_networks import SUPPORTED_NETWORKS
from utils.fetch_pool import fetch_pool_data
from utils.simulate_earnings import simulate_apr_apy, format_small_number
from utils.chart_analysis import fetch_closing_prices
from utils.pair_analysis import get_support_resistance_from_pair
from external_aprs.unified_apr import get_best_real_apr
import logging

logger = logging.getLogger("ZenPool")
logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler("zenpool_debug.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

SYMBOL_MAP = {
    "sol": "solana",
    "eth": "ethereum",
    "btc": "bitcoin",
    "usdc": "usd-coin",
    "usdt": "tether",
    "matic": "polygon",
    "bnb": "binancecoin",
    "ada": "cardano",
    "dot": "polkadot",
    "avax": "avalanche-2",
    "link": "chainlink",
    "op": "optimism",
    "arb": "arbitrum",
    "doge": "dogecoin"
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

            pair_address = info.get("pair_address") or info.get("address")
            logger.debug(f"Using pair address: {pair_address}")
            zones = get_support_resistance_from_pair(pair_address)

            if zones:
                support = zones["support"]
                resistance = zones["resistance"]
                logger.debug(f"Support: {support}, Resistance: {resistance}")
                range_span = resistance - support if resistance > support else 0.0001
                passive_apr = round((info["volume_usd"] / info["liquidity_usd"]) * (range_span / info["price_usd"]) * 100, 2)
                price_range = {
                    "lower": support,
                    "upper": resistance,
                    "confidence": "Support/Resistance based on DEX pair chart"
                }
                apr_value = round(passive_apr, 2) if not real_apr_info else apr_value
            else:
                logger.warning("Fallback triggered: no support/resistance zones")
                price_range = {
                    "lower": info["price_usd"],
                    "upper": info["price_usd"],
                    "confidence": "⚠️ Could not estimate support/resistance from DEX chart"
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
