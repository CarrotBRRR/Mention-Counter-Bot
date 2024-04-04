import os, json, sys
import operator as op
import random as rand
import discord as dc
import typing

from discord.ext import commands as comms
from discord.utils import get
from dotenv import load_dotenv

from Guild import Guild
from GlobalLogger import GlobalLogger

intents = dc.Intents.default()
intents.message_content = True
intents.members = True

bot = comms.Bot(command_prefix='q.', intents=intents)

load_dotenv()

global l
l = GlobalLogger()

global guilds
guilds: dict[str, Guild] = {}

@bot.event
async def on_ready():
    l.log(f'Logged in as {bot.user.name}')
    l.log(f'[INFO] Setting up Guilds...')

    # Empty the guilds dictionary
    guilds: dict[str, Guild] = {}

    for guild in bot.guilds:
        # Create a directory for the guild if it doesn't exist
        if not os.path.exists(guild_folder):
            os.mkdir(guild_folder)
            os.makedirs(guild_folder, exist_ok=True)
            l.log(f'\t[INFO] Created Directory for {guild.name}')

        # Create a Guild object for the guild
        guilds[str(guild.id)] = Guild(guild)
        guild_folder = f'./data/{guild.id}'
        l.log(f'\t[INFO] Created Guild Object for {guild.name}')
    
    l.log(f'[INFO] Guilds Setup Complete!')

# ------------------------- Message Events ------------------------- #

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    text = str(message.content).replace("\n","\n\t")
    l.log(f'+ [{message.guild}] ({message.channel}) {message.author}: {text}')

    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or after.author.bot:
        return

    before_text = str(before.content).replace("\n","\n\t")
    after_text = str(after.content).replace("\n","\n\t")

    l.log(f'* [{before.guild}] ({before.channel}) {before.author} edited message:\n\t   {before_text.content}\n\t-> {after_text.content}')

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    text = str(message.content).replace("\n","\n\t")
    l.log(f'- [{message.guild}] ({message.channel}) {message.author}: {text}')

# ------------------------- Guild Events ------------------------- #

@bot.event
async def on_guild_join(guild):
    l.log(f'[INFO] Joined Guild: {guild.name}!\n Setting up Guild...')

    guild_folder = f'./data/{guild.id}'
    if not os.path.exists(guild_folder):
        os.mkdir(guild_folder)
        os.makedirs(guild_folder, exist_ok=True)
        l.log(f'\t[INFO] Created Directory for {guild.name}')
    
    guilds[str(guild.id)] = Guild(guild)

    l.log(f'[INFO] Guild Setup for {guild.name} Complete!')

bot.remove_command('help')
bot.run(os.getenv('TOKEN'))