import os, json
import operator as op
import random as rand
import discord as dc
from discord.ext import commands as comms
from discord.utils import get
from dotenv import load_dotenv

from GuildInfo import GuildInfo

# ------------------------------------ Globals ------------------------------------
load_dotenv()

intents = dc.Intents.default()
intents.message_content = True
intents.members = True
bot = comms.Bot(command_prefix="q.", intents=intents)

global guilds
global message_buffer

# ----------------------------------- Functions -----------------------------------
# Retrieves config for ctx
async def getConfig(ctx):
    path = f'./data/{ctx.guild.id}'
    filepath = os.path.join(path, 'ServerInfo.json')

    with open(filepath) as f:
        config = json.loads(f)

    return config

# Edits the given config, attribute to change 
# and newdata to change
async def editConfig(ctx, config, attribute, newdata):
    path = f'./data/{ctx.guild.id}'
    filepath = os.path.join(path, 'ServerInfo.json')
    config[attribute] = newdata

    with open(filepath, 'w+') as f:
        json.dump(config, f, indent=4)

    return 0

# Retrieves GuildInfo Class object with matching ID
# Creates a new GuildInfo if not found
async def getGuildInfo(ctx):
    print(f'Getting Guild Data for {ctx.guild}...')
    for data in guilds:
        if data.id == ctx.guild.id:
            print('Retrieved Guild Data!')
            return data
    
    print('Could not find Guild Data, Creating...')
    data = GuildInfo(ctx.guild.name, ctx.guild.id)
    guilds.append(data)
    print('Created!')
    return data

# Retrieves Messages from Quotes Channel and stores it in 
# the messages attribute of GuildInfo class object
async def getQuotes(ctx):
    data = getGuildInfo(ctx)
    config = getConfig(ctx)

    channel = dc.utils.get(ctx.guild.channels, config["Q Channel"])

    print(f'Retrieving Quotes for {ctx.guild} in {channel}')
    async for message in channel.history(limit=None):
        data.messages.append(message)
    data.messages.reverse()
    print('Quotes Retrieved!')

# Counts amount of times mentioned in 
# the cached messages in GuildInfo class object
async def count(ctx):
    guild_info = getGuildInfo(ctx)
    counts = []

    print(f'Beginning Quote Count for {ctx.guild.name}...')
    for member in ctx.guild.members:
        if not member.bot:
            c = 0
            a = 0
            for message in guild_info.messages:
                if member in message.mentions:
                    c += 1
                if member == message.author and len(message.mentions) >= 1:
                    a += 1
        if c > 0 or a > 0:
            # Create an object of member and counts
            obj = {
                "Name": str(member.name),
                "Mentions": int(c),
                "Authored": int(a)
            }
        counts.append(obj)
    print('Finished Counting!')

    print('Saving Scores...')
    path = f'./data/{ctx.guild.id}'
    filepath = os.path.join(path, 'Leaderboard.json')

    counts.sort(key=op.itemgetter('Mentions'), reverse=True)

    with open(filepath, 'w+', encoding="utf-8") as f:
        json.dump(counts, f, indent=4)

    print('Scores Saved!')
    return counts

# Retrieves scores from the Leaderboard.json
async def getScores(ctx):
    print('Getting Scores...')
    # Load JSON containing Scores
    path = f'./data/{ctx.guild.id}'
    filepath = os.path.join(path, 'Leaderboard.json')

    with open(filepath, 'r') as f:
        users = json.load(f)

    # Initialize Scores Array
    Scores = []

    for user in users:
        # Extract Data from JSON
        Name = user["Name"]
        Count = int(user["Mentions"])
        Authored = int(user["Authored"])

        Scores.append([Name, Count, Authored])

    print('Scores Retrieved!')
    
    return Scores

async def createLB(ctx):
    scores = await getScores(ctx)
    index = 1

    em = dc.Embed(title='Most Quoted Members:', color=0xffbf00)
    for user in scores:
        em.add_field(name=f'{index}. {user[index-1][0]}',
                        value=f'{user[index-1][1]} Quotes',
                        inline=False)
        index += 1
    em.set_footer(text="Brought to you by: CarrotBRRR")

    return em
# ----------------------------------- Bot Events ----------------------------------
@bot.event
async def on_ready():
    print(f'Initializing Files...')

    # Initialize data folder
    if not os.path.exists("./data"):
        os.mkdir('./data')

    # Initialize an array of guilds
    guilds = []

    for guild in bot.guilds:

        # Create a GuildInfo Class Object
        guilds.append[GuildInfo(guild.name, guild.id)]

        # Get Path for specific guild
        path = f'./data/{guild.id}'

        # Set-up Directory and Config
        if not os.path.exists(path):
            print(f'Setting up Directory for {guild.name}...')
            os.mkdir(path)

            # Set-up Default Config JSON
            info = {
                "Name" : str(guild.name),
                "Guild ID" : int(guild.id),
                "Q Channel" : int(0),
                "LB" : {
                    "Channel ID" : int(0),
                    "Message ID" : int(0)
                }
            }

            # Write to a File
            with open(os.path.join(path, 'ServerInfo.json'), 'w+') as f:
                json.dumps(info, f, indent=4)
                
            print(f'Directory for {guild.name} initialized!')
            
    print(f'Bot connected as {bot.user}')

@bot.event
@comms.has_permissions(administrator=True)
async def on_message(message):
    print(f'{message.guild} {message.channel} {message.author}: {message.content}')

    if message.content.startswith("q."):
        print("Command Detected!")

        await bot.process_commands(message)
        return

# --------------------------------- Bot Commands ----------------------------------


# -------------------------------- Admin Commands ---------------------------------
    
# Command to set q channel
# q.setQChannel [channel ID]
@bot.command()
@comms.has_permissions(administrator=True)
async def setQChannel(ctx):
    if len(ctx.message.channel_mentions == 1):
        print("Setting up default channel...")

        config = getConfig(ctx)
        editConfig(ctx, config, "Q Channel", ctx.message.raw_channel_mentions)

        print(f'Q Channel for {ctx.guild.id} is now {ctx.get_channel(config["Q Channel"])}')

    else: 
        print("invalid number of channels")

@bot.command()
@comms.has_permissions(administrator=True)
async def initLB(ctx):
    em = await createLB()
    lb = await ctx.send(embed=em)
    config = getConfig(ctx)
    lbobj = {
        "Channel ID" : int(lb.get_channel().id),
        "Message ID" : int(lb.id)
    }

    editConfig(ctx, config, "LB", lbobj)


bot.remove_command('help')
bot.run(os.getenv('TOKEN'))