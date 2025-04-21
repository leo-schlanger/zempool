import discord
from discord import app_commands

class HelpCommand(app_commands.Command):
    def __init__(self):
        async def callback(interaction: discord.Interaction):
            await interaction.response.send_message(
                "**ZenPool Help 🧘**\n\n"
                "Use `/zenpool generate <network> <pair>` to analyze a pool.\n"
                "Start typing a network name and use auto-complete suggestions.\n\n"
                "**How APR and APY are calculated:**\n"
                "- Real APR is fetched from Beefy/Velodrome/Thena.\n"
                "- Estimated APR is based on volume/liquidity.\n"
                "- APY is compounded daily from APR.\n\n"
                "*Note: gas fees and impermanent loss are not included.*"
            )

        super().__init__(
            name="help",
            description="Show usage instructions",
            callback=callback,
        )
