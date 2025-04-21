import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging
from commands.generate import ZenPoolCommands
from commands.help import HelpCommand

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ZenPool")

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    logger.info(f"ZenPool is online as {bot.user}")
    try:
        tree.add_command(ZenPoolCommands(name="zenpool", description="ZenPool analysis commands"))
        tree.add_command(HelpCommand(name="zenpool", description="ZenPool help"))

        synced = await tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")

bot.run(TOKEN)