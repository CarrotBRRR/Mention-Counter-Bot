import os, json
import operator as op
import random as rand
import discord as dc
from discord.ext import commands as comms
from discord.utils import get
from dotenv import load_dotenv

from GuildData import GuildData

load_dotenv()

intents = dc.Intents.default()
intents.message_content = True
intents.members = True
bot = comms.Bot(command_prefix="q.", intents=intents)

# ------------------------------------- Globals -------------------------------------
global guilds
global messages

# ------------------------------------- Functions -------------------------------------
async def getMessages(ctx):
    print(f'Retrieving Message History for {ctx.guild} in {ctx.channel}')


async def getConfig(ctx):
    path = f'./data/{ctx.guild.id}'
    filepath = os.path.join(path, 'ServerInfo.json')

    with open(filepath) as f:
        config = json.loads(f)

    return config

async def editConfig(ctx, config, attribute, data):
    path = f'./data/{ctx.guild.id}'
    filepath = os.path.join(path, 'ServerInfo.json')
    config[attribute] = data

    with open(filepath, 'w') as f:
        json.dump(config, f, indent=4)

    return 0

# ------------------------------------- Bot Events -------------------------------------
@bot.event
async def on_ready():
    print(f'Initializing Files...')

    # Initialize data folder
    if not os.path.exists("./data"):
        os.mkdir('./data')

    # Initialize an array of guilds
    guilds = []

    for guild in bot.guilds:

        guilds.append[GuildData(guild.name, guild.id)]

        # Get Path for specific guild
        path = f'./data/{guild.id}'
        if not os.path.exists(path):
            print(f'Setting up Directory for {guild.name}...')
            os.mkdir(path)

            # Set up Default Config JSON
            info = {
                "Name" : str(guild.name),
                "Guild ID" : int(guild.id),
                "Q Channel" : int(0),
                "LB Message" : {
                    "Channel ID" : int(0),
                    "Message ID" : int(0)
                }
            }

            # Write File
            with open(os.path.join(path, 'ServerInfo.json'), 'w+') as f:
                json.dumps(info, f, indent=4)
                
            print(f'Directory for {guild.name} initialized!')
            
    print(f'Bot connected as {bot.user}')

@bot.event
async def on_message(message):
    print(f'{message.guild} {message.channel} {message.author}: {message.content}')

    ctx = message.get_context()

    if message.content.startswith("q."):
        print("Command Detected!")

        await bot.process_commands(message)
        return

# ------------------------------------- Bot Commands -------------------------------------

# Command to set q channel
# q.setQChannel [channel ID]
@bot.command()
async def setQChannel(message):
    if len(message.channel_mentions == 1):
        print("Setting up default channel...")

        ctx = message.get_context()

        config = getConfig(ctx)
        editConfig(ctx, config, "Q Channel", message.raw_channel_mentions)

        print(f'Q Channel for {ctx.guild.id} is now {ctx.get_channel(config["Q Channel"])}')

    else: 
        print("invalid number of channels")


bot.remove_command('help')
bot.run(os.getenv('TOKEN'))