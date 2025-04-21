import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv
from commands import ZenPoolCommands
from keep_alive import keep_alive

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ZenPool")

load_dotenv()
keep_alive()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    logger.info(f"ZenPool is online as {bot.user}")
    try:
        tree.add_command(ZenPoolCommands())
        synced = await tree.sync()
        logger.info(f"Synced {len(synced)} commands")
    except Exception as e:
        logger.error(f"Sync failed: {e}")

keep_alive()
if __name__ == "__main__":
    bot.run(TOKEN)