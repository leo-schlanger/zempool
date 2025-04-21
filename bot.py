import discord
from discord.ext import commands
from discord import app_commands
import os
import logging
from dotenv import load_dotenv

from utils.fetch_pool import fetch_pool_data
from utils.chart_analysis import get_historical_prices_stub, suggest_price_range
from utils.simulate_earnings import simulate_apr_apy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ZenPool")

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

SUPPORTED_NETWORKS = [
    "ethereum", "bsc", "polygon", "arbitrum", "optimism", "base", "avalanche",
    "fantom", "solana", "cronos", "zksync", "mantle", "linea", "celo",
    "moonbeam", "moonriver", "harmony", "blast", "sonic", "scroll", "berachain", "monad"
]

async def network_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=net, value=net)
        for net in SUPPORTED_NETWORKS
        if current.lower() in net.lower()
    ][:25]

class ZenPoolCommands(app_commands.Group):
    @app_commands.command(name="generate", description="Analyze a pair and simulate LP returns")
    @app_commands.describe(network="Blockchain network", pair="Pair address (contract)")
    @app_commands.autocomplete(network=network_autocomplete)
    async def generate(self, interaction: discord.Interaction, network: str, pair: str):
        await interaction.response.defer()
        logger.info(f"Running analysis for network={network}, pair={pair}")

        dex_url = f"https://dexscreener.com/{network}/{pair}"
        info = fetch_pool_data(dex_url)
        if isinstance(info, str):
            await interaction.followup.send(info)
            return

        prices = get_historical_prices_stub(float(info["price_usd"]))
        price_range = suggest_price_range(prices)
        earnings = simulate_apr_apy(info["apr"], info["volume_usd"], info["liquidity_usd"])

        range_msg = (
            f"**📈 Recommended LP Range:**  \n"
            f"`$ {price_range['lower']}` — `$ {price_range['upper']}`  \n"
            f"*Confidence: {price_range['confidence']}*"
        ) if price_range else "Could not determine a stable price range."

        earnings_msg = (
            f"**💸 Simulated Earnings for $100 Deposit**\n\n"
            f"**APR (Simple Interest):**\n"
            f"• Daily: `$ {earnings['apr']['daily']}`\n"
            f"• Monthly: `$ {earnings['apr']['monthly']}`\n"
            f"• Yearly: `$ {earnings['apr']['yearly']}`\n\n"
            f"**APY (Compounded Daily):**\n"
            f"• Daily: `$ {earnings['apy']['daily']}`\n"
            f"• Monthly: `$ {earnings['apy']['monthly']}`\n"
            f"• Yearly: `$ {earnings['apy']['yearly']}`"
        ) if earnings else "Could not simulate earnings. Invalid APR data."

        msg = (
            f"**🧘 ZenPool Analysis Complete!**\n\n"
            f"**Pair:** {info['pair']}\n"
            f"**Network:** {info['network']}\n"
            f"**DEX:** {info['dex']}\n"
            f"**Current Price:** `$ {float(info['price_usd']):,.4f}`\n"
            f"**24h Volume:** `$ {float(info['volume_usd']):,.2f}`\n"
            f"**Liquidity:** `$ {float(info['liquidity_usd']):,.2f}`\n"
            f"**Estimated APR:** {info['apr']}\n\n"
            f"{range_msg}\n\n"
            f"{earnings_msg}\n\n"
            f"*Note: gas fees and impermanent loss are not included.*"
        )

        await interaction.followup.send(msg)

    @app_commands.command(name="help", description="Show usage instructions")
    async def help(self, interaction: discord.Interaction):
        logger.info("Received /zenpool help command.")
        await interaction.response.send_message(
            "**ZenPool Bot Help 🧘**\n\n"
            "Use `/zenpool generate <network> <pair>` to analyze a pool.\n"
            "Start typing a network name and use auto-complete suggestions.\n"
            "Example: `/zenpool generate sonic 0x...`"
            "🔍 **How APR and APY are calculated:**"
            "- **APR Estimated**: calculated from 24h volume and pool liquidity, assuming 0.3% trading fees."
            "- **APR Real**: pulled from Beefy, Velodrome, or Thena if matched by address."
            "- **APY**: compounded version of the APR, calculated daily/monthly/yearly."
        )

@bot.event
async def on_ready():
    logger.info(f"ZenPool is online as {bot.user}")
    try:
        tree.add_command(ZenPoolCommands(name="zenpool", description="ZenPool analysis commands"))
        synced = await tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")

bot.run(TOKEN)