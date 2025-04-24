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
            "Use `/zenpool generate <network> <pair>` to analyze LPs.\n"
            "- APR is estimated via volume/liquidity or real source if available.\n"
            "- APY is calculated from APR.\n"
            "*Gas fees and IL not included.*"
        )
