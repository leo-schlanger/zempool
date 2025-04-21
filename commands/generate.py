import discord
from discord import app_commands
from config.supported_networks import SUPPORTED_NETWORKS
from utils.fetch_pool import fetch_pool_data
from utils.simulate_earnings import simulate_apr_apy, format_small_number
from utils.chart_analysis import get_historical_prices_stub, suggest_price_range
from external_aprs.unified_apr import get_best_real_apr
import logging

logger = logging.getLogger("ZenPool")

async def network_autocomplete(interaction: discord.Interaction, current: str):
    try:
        return [app_commands.Choice(name=net, value=net) for net in SUPPORTED_NETWORKS if current.lower() in net.lower()][:25]
    except Exception as e:
        logger.error(f"Autocomplete error: {e}")
        return []

class ZenPoolCommands(app_commands.Group):
    @app_commands.command(name="generate", description="Analyze a pair and simulate LP returns")
    @app_commands.describe(network="Blockchain network", pair="Pair address (contract)")
    @app_commands.autocomplete(network=network_autocomplete)
    async def generate(self, interaction: discord.Interaction, network: str, pair: str):
        if interaction.is_expired():
            logger.error("❌ Interaction expired before processing.")
            return

        logger.info(f"Running analysis for network={network}, pair={pair}")

        try:
            await interaction.response.defer(thinking=True)
        except discord.NotFound:
            logger.error("❌ Could not defer — interaction not found.")
            return
        except Exception as e:
            logger.error(f"ZenPool: Defer error: {e}")
            return

        try:
            info = fetch_pool_data(f"{network}/{pair}")
            if isinstance(info, str):
                await interaction.followup.send(info)
                return

            real_apr_info = get_best_real_apr(pair, network)
            real_apr_line = (
                f"🔥 Real APR from {real_apr_info['source']}: `{real_apr_info['apr']}%`\n<{real_apr_info['url']}>"
                if real_apr_info else "🧠 No farming APR found. Estimated only from trading volume."
            )

            prices = get_historical_prices_stub(float(info["price_usd"]))
            price_range = suggest_price_range(prices)

            earnings = simulate_apr_apy(
                real_apr_info['apr'] if real_apr_info else info["apr"],
                info["volume_usd"],
                info["liquidity_usd"]
            )

            if earnings is None:
                await interaction.followup.send("❌ An error occurred: APR calculation failed.")
                return

            range_msg = (
                f"**📈 Recommended LP Range:**  \n"
                f"`$ {format_small_number(price_range['lower'])}` — `$ {format_small_number(price_range['upper'])}`  \n"
                f"*Confidence: {price_range['confidence']}*"
            ) if price_range else "Could not determine a stable price range."

            earnings_msg = (
                f"**💸 Simulated Earnings for $100 Deposit**\n\n"
                f"**APR Return:**\n"
                f"• Daily: `$ {earnings['apr_return_usd']['daily']}`\n"
                f"• Monthly: `$ {earnings['apr_return_usd']['monthly']}`\n"
                f"• Yearly: `$ {earnings['apr_return_usd']['yearly']}`\n\n"
                f"**APY (Compounded):**\n"
                f"• Daily: `{earnings['apy_percent']['daily']}%`\n"
                f"• Monthly: `{earnings['apy_percent']['monthly']}%`\n"
                f"• Yearly: `{earnings['apy_percent']['yearly']}%`"
            )

            msg = (
                f"**🧘 ZenPool Analysis Complete!**\n\n"
                f"**Pair:** {info['pair']}\n"
                f"**Network:** {info['network']}\n"
                f"**DEX:** {info['dex']}\n"
                f"**Current Price:** `$ {format_small_number(float(info['price_usd']))}`\n"
                f"**24h Volume:** `$ {float(info['volume_usd']):,.2f}`\n"
                f"**Liquidity:** `$ {float(info['liquidity_usd']):,.2f}`\n"
                f"{real_apr_line}\n\n"
                f"{range_msg}\n\n"
                f"{earnings_msg}\n\n"
                f"*Note: gas fees and impermanent loss are not included.*"
            )

            await interaction.followup.send(msg)

        except Exception as e:
            logger.error(f"ZenPool Error: {e}")
            await interaction.followup.send("❌ An unexpected error occurred during analysis.")