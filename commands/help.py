import discord
from discord import app_commands
import logging

logger = logging.getLogger("ZenPool")

class HelpCommand(app_commands.Group):
    @app_commands.command(name="help", description="Show usage instructions")
    async def help(self, interaction: discord.Interaction):
        logger.info("Received /zenpool help command.")
        await interaction.response.send_message(
            "**ZenPool Bot Help 🧘**\n\n"
            "Use `/zenpool generate <network> <pair>` to analyze a liquidity pool.\n"
            "Start typing the name of a blockchain to get autocomplete options.\n"
            "Example: `/zenpool generate sonic 0x...`\n\n"
            "🔍 **How APR and APY are calculated:**\n"
            "- **Estimated APR**: Based on 24h trading volume and liquidity, using a 0.3% fee assumption.\n"
            "- **Real APR**: Pulled from Beefy if the pool is found in their vaults.\n"
            "- **APY**: Compounded APR, simulated for daily, monthly, and yearly yields.\n\n"
            "💡 *Note: gas fees and impermanent loss are not included in simulations.*"
        )
