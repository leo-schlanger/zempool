import discord
from discord import app_commands
from config.supported_networks import SUPPORTED_NETWORKS
from utils.fetch_pool import fetch_pool_data
from utils.simulate_earnings import simulate_apr_apy, format_small_number
from utils.chart_analysis import fetch_closing_prices, suggest_price_range
from external_aprs.unified_apr import get_best_real_apr
import logging

logger = logging.getLogger("ZenPool")

async def network_autocomplete(interaction: discord.Interaction, current: str):
    logger.info("Autocomplete triggered for network with current input: %s", current)
    return [
        app_commands.Choice(name=net, value=net)
        for net in SUPPORTED_NETWORKS if current.lower() in net.lower()
    ][:25]

class GenerateCommand(app_commands.Command):
    def __init__(self):
        async def callback(interaction: discord.Interaction, network: str, pair: str):
            try:
                await interaction.response.defer(thinking=True)
                info = fetch_pool_data(network, pair)
                if isinstance(info, str):
                    await interaction.followup.send(info)
                    return

                real_apr_info = get_best_real_apr(pair, network)
                real_apr_line = (
                    f"🔥 Real APR from {real_apr_info['source']}: `{real_apr_info['apr']}%`\n<{real_apr_info['url']}>"
                    if real_apr_info else "🧠 No farming APR found. Estimated only from trading volume."
                )

                prices = fetch_closing_prices(info["pair"].split("/")[0].lower())
                price_range = suggest_price_range(prices)
                apr_value = real_apr_info['apr'] if real_apr_info else info.get("apr")

                if apr_value is None:
                    await interaction.followup.send("❌ Could not retrieve APR data for this pool.")
                    return

                earnings = simulate_apr_apy(apr_value, info["volume_usd"], info["liquidity_usd"])
                if earnings is None:
                    await interaction.followup.send("❌ An error occurred: APR calculation failed.")
                    return

                msg = (
                    f"**🧘 ZenPool Analysis Complete!**\n\n"
                    f"**Pair:** {info['pair']}\n"
                    f"**Network:** {info['network']}\n"
                    f"**DEX:** {info['dex']}\n"
                    f"**Current Price:** `$ {format_small_number(float(info['price_usd']))}`\n"
                    f"**24h Volume:** `$ {float(info['volume_usd']):,.2f}`\n"
                    f"**Liquidity:** `$ {float(info['liquidity_usd']):,.2f}`\n"
                    f"{real_apr_line}\n\n"
                    f"**📈 Recommended LP Range:**\n"
                    f"`$ {format_small_number(price_range['lower'])}` — `$ {format_small_number(price_range['upper'])}`\n"
                    f"*Confidence: {price_range['confidence']}*\n\n"
                    f"**💸 Simulated Earnings for $100 Deposit**\n\n"
                    f"**APR Return:**\n"
                    f"• Daily: `$ {earnings['apr_return_usd']['daily']}`\n"
                    f"• Monthly: `$ {earnings['apr_return_usd']['monthly']}`\n"
                    f"• Yearly: `$ {earnings['apr_return_usd']['yearly']}`\n\n"
                    f"**APY (Compounded):**\n"
                    f"• Daily: `{earnings['apy_percent']['daily']}%`\n"
                    f"• Monthly: `{earnings['apy_percent']['monthly']}%`\n"
                    f"• Yearly: `{earnings['apy_percent']['yearly']}%`\n\n"
                    f"*Note: gas fees and impermanent loss are not included.*"
                )
                await interaction.followup.send(msg)

            except Exception as e:
                logger.error(f"ZenPool Error: {e}")
                await interaction.followup.send("❌ An unexpected error occurred during analysis.")

        super().__init__(
            name="generate",
            description="Analyze a pair and simulate LP returns",
            callback=callback,
        )
        self.autocomplete = {"network": network_autocomplete}
