import os, json
import operator as op
import random as rand
import discord as dc
from discord.ext import commands as comman
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()

intents = dc.Intents.default()
intents.message_content = True
intents.members = True
bot = comman.Bot(command_prefix="q.", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')
    if not os.path.exists("./data"):
        os.mkdir('./data')

    for guild in bot.guilds:
        path = f'./data/{guild.id}'
        if not os.path.exists(path):
            print(f'Making Directory for {guild}')
            os.mkdir(path)
            with open(os.path.join(path, 'ServerInfo.json'), 'w+') as f:
                info = {
                    "Name" : str(guild.name),
                    "Guild ID" : int(guild.id),
                    "Q Channel" : int(None),
                    "LB Message" : {
                        "Channel ID" : int(0),
                        "Message ID" : int(0)
                    }
                }

@bot.event
async def on_message(message):
    print(f'{message.guild} {message.channel} {message.author}: {message.content}')

    ctx = message.get_context()

    if message.content.startswith("q."):
        print("Command Detected!")

        await bot.process_commands(message)
        return


# Command to set q channel
@bot.command()
async def setQChannel(message):
    if len(message.channel_mentions == 1):
        print("Setting up default channel...")

        ctx = message.get_context()
        path = f'./data/{ctx.guildID}'
        filepath = os.path.join(path, 'ServerInfo.json')

        with open(filepath) as f:
            config = json.loads(f)

        config["Q Channel"] = message.channel_mentions[0]

        print(f'Q Channel set to {config["Q Channel"]}')

    else: 
        print("invalid number of channels")




bot.remove_command('help')
bot.run(os.getenv('TOKEN'))