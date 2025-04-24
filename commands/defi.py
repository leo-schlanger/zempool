import discord
from discord import app_commands
from utils.defillama import list_defillama_protocols
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class DefiTopCommand(app_commands.Command):
    def __init__(self):
        super().__init__(
            name="defi",
            description="List top DeFi protocols by TVL (via DefiLlama)",
            callback=self.callback
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        protocols = list_defillama_protocols()
        if not protocols:
            await interaction.followup.send("❌ Failed to fetch DeFi protocol data.")
            return

        top_protocols = sorted(protocols, key=lambda x: x.get("tvl", 0), reverse=True)[:10]

        embed = discord.Embed(
            title="🌐 Top DeFi Protocols (TVL)",
            description="Data via [DefiLlama](https://defillama.com)",
            color=0x2ecc71
        )

        for proto in top_protocols:
            name = proto.get("name", "Unknown")
            tvl = f"$ {proto.get('tvl', 0):,.0f}"
            chains = ", ".join(proto.get("chains", [])[:3]) or "N/A"
            category = proto.get("category", "Uncategorized")
            change = proto.get("change_7d", 0)

            embed.add_field(
                name=f"{name} ({category})",
                value=f"TVL: {tvl}\nChains: {chains}\n7d: {change:.2f}%",
                inline=False
            )

        await interaction.followup.send(embed=embed)
