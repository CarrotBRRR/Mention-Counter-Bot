import os, sys
import discord as dc
from discord.ext import commands
from dotenv import load_dotenv

from GuildInfo import GuildInfo
from storage import store, setup_guild

# ------------------------------------ Globals ------------------------------------
load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

intents = dc.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="q.", intents=intents)

# Runtime cache
guilds = []

# ----------------------------------- Events --------------------------------------
@bot.event
async def on_ready():
    global guilds
    guilds = []

    for guild in bot.guilds:
        guilds.append(GuildInfo(guild.name, guild.id))
        await setup_guild(guild)

    print(f"[INFO] Bot connected as {bot.user}")

@bot.event
async def on_guild_join(guild):
    guilds.append(GuildInfo(guild.name, guild.id))
    await setup_guild(guild)

# ----------------------------------- Startup -------------------------------------
async def load_cogs():
    for cog in ["quotes", "leaderboard", "admin"]:
        await bot.load_extension(f"cogs.{cog}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("TOKEN"))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
