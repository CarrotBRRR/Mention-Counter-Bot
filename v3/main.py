import os, json, sys
import operator as op
import random as rand
import discord as dc
import typing

from discord.ext import commands as comms
from discord.utils import get
from dotenv import load_dotenv
import datetime

intents = dc.Intents.default()
intents.message_content = True
intents.members = True

bot = comms.Bot(command_prefix='q.', intents=intents)

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

def log(message):
    print(f'{message}')
    with open(logfile_path, 'a') as log_file:
        log_file.write(f'{message}\n')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

    current_time = datetime.datetime.now()
    logfile = f'{current_time.strftime("%Y-%m-%d_%H-%M-%S")}.log'

    global logfile_path
    logfile_path = os.path.join(guild_folder, logfile)

    log(f'[INFO] Setting up Directory for {guild.name}...')

    for guild in bot.guilds:
        guild_folder = f'./data/{guild.id}'
        if not os.path.exists(guild_folder):
            log(f'[INFO] Setting up Directory for {guild.name}...')
            os.mkdir(guild_folder)
            os.makedirs(guild_folder, exist_ok=True)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Rest of your message processing logic goes here

    await bot.process_commands(message)

bot.remove_command('help')
bot.run(os.getenv('TOKEN'))