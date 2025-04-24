import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv
from commands.group import ZenPoolGroup
from keep_alive import keep_alive

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ZenPool")

load_dotenv()
keep_alive()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    logger.info(f"ZenPool is online as {bot.user}")
    try:
        tree.add_command(ZenPoolGroup())
        synced = await tree.sync()
        logger.info(f"✅ Synced {len(synced)} commands.")
    except Exception as e:
        logger.error(f"[SYNC ERROR] {e}")

if __name__ == "__main__":
    bot.run(TOKEN)