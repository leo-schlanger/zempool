from discord import app_commands, Embed
import logging

logger = logging.getLogger("ZenPool")

def show_help(func):
    @app_commands.command(name="help", description="Show usage instructions")
    async def wrapper(self, interaction):
        logger.info("Received /zenpool help command.")

        embed = Embed(title="🧘 ZenPool Help", color=0x1ABC9C)
        embed.add_field(
            name="How to use",
            value="Use `/zenpool generate <network> <pair>` to analyze a pool.\nExample: `/zenpool generate sonic 0x...`",
            inline=False
        )
        embed.add_field(
            name="APR vs APY",
            value="- **Estimated APR** = from volume and liquidity\n- **Real APR** = pulled from Beefy if matched\n- **APY** = compounded daily/monthly/yearly",
            inline=False
        )
        embed.set_footer(text="Note: Gas fees and impermanent loss are not included.")

        await interaction.response.send_message(embed=embed)
    return wrapper