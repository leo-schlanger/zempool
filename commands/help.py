import logging
logger = logging.getLogger("help")
logger.setLevel(logging.DEBUG)
import discord
from discord import app_commands

class HelpCommand(app_commands.Command):
    def __init__(self):
        super().__init__(
            name="help",
            description="Show help for ZenPool",
            callback=self.callback
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "**ZenPool Help 🧘**\n\n"
            "**/zenpool generate <network> <pair>**\n"
            "🔹 Analyze LPs using on-chain data from DexScreener\n"
            "🔹 Calculates APR from volume, liquidity, and fee rate\n"
            "🔹 Tries to fetch real fee-based APR from DefiLlama if available\n"
            "🔹 Generates a range around the price based on volume stability\n"
            "🔹 Shows potential earnings on $1000 LP deposit\n\n"
            "**/zenpool defi**\n"
            "🌐 Discover top DeFi protocols by Total Value Locked (TVL)\n"
            "🔹 Shows name, category, chains, TVL, and 7d change\n"
            "🔹 Data powered by DefiLlama\n\n"
            "*Note: All earnings estimations exclude gas fees and impermanent loss.*"
        )
