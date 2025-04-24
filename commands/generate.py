import discord
from discord import app_commands
from config.supported_networks import SUPPORTED_NETWORKS
from handlers.interaction import analyze_pair
import logging

logger = logging.getLogger("ZenPool")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("zenpool_debug.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Esta função de autocomplete pode ser usada por qualquer comando
async def network_autocomplete(interaction: discord.Interaction, current: str):
    try:
        return [
            app_commands.Choice(name=net, value=net)
            for net in SUPPORTED_NETWORKS
            if current.lower() in net.lower()
        ][:25]
    except Exception as e:
        logger.error(f"[autocomplete] Error: {e}")
        return []

# Exporta o comando formatado como função decorada
def get_generate_command():
    @app_commands.command(
        name="generate",
        description="Analyze a pair and simulate LP returns"
    )
    @app_commands.describe(
        network="Blockchain network (e.g., ethereum, bsc, optimism)",
        pair="Token pair (e.g., USDC-ETH)"
    )
    async def generate(interaction: discord.Interaction, network: str, pair: str):
        await interaction.response.defer(thinking=True)
        await analyze_pair(interaction, network, pair)

    generate.autocomplete("network")(network_autocomplete)
    return generate