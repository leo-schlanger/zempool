
import discord
from discord.ext import commands
import logging

logger = logging.getLogger("ZenPool")

class ReanalyzeView(discord.ui.View):
    def __init__(self, bot: commands.Bot, network: str, pair: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.network = network
        self.pair = pair

    @discord.ui.button(label="🔁 Reanalyze", style=discord.ButtonStyle.secondary, custom_id="reanalyze_button")
    async def reanalyze_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        logger.info(f"[BUTTON] Reanalyze triggered for {self.network} / {self.pair}")
        try:
            command = self.bot.tree.get_command("generate")
            await command.callback(interaction, network=self.network, pair=self.pair)
        except Exception as e:
            logger.error(f"[BUTTON] Reanalyze failed: {e}")
            await interaction.response.send_message("❌ Could not reanalyze.", ephemeral=True)
