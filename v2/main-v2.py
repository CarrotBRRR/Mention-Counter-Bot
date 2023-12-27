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

# Retrieves Messages that Mention the specified user
async def getMentions(ctx, member):
    data = getGuildInfo(ctx)
    config = getConfig(ctx)
    channel = dc.utils.get(ctx.guild.channels, config["Q Channel"])

    quote = ""
    quotes = ""
    print(f'Searching for mentions of {member.name} in {channel}...')

    for message in data.messages:
        if member in message.mentions:
            quote = str(message.content)
            for mentioned in message.mentions:
                quote = quote.replace(f'<@!{mentioned.id}>', f'@{mentioned.name}').replace(f'<@{mentioned.id}>', f'@{mentioned.name}')
            
            quotes += quote + "\n\n"

    print('All mentions Found!')
    
    with open(f'./data/{ctx.guild}/dump.txt', 'w+', encoding='utf-8') as d:
        d.write(quotes)

async def getAuthoured(ctx, member):
    data = getGuildInfo(ctx)
    config = getConfig(ctx)
    channel = dc.utils.get(ctx.guild.channels, config["Q Channel"])

    quote = ""
    quotes = ""
    print(f'Searching for Author {member.name} in {channel}...')

    for message in data.messages:
        if member == message.author and len(message.mentions) >= 1:
            quote = str(message.content)
            for mentioned in message.mentions:
                quote = quote.replace(f'<@!{mentioned.id}>', f'@{mentioned.name}').replace(f'<@{mentioned.id}>', f'@{mentioned.name}')
            
            quotes += quote + "\n\n"

    print(f'All quotes by author {member.name} Found!')

    with open(f'./data/{ctx.guild}/dump.txt', 'w+', encoding='utf-8') as f:
        f.write(quotes)

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
                if member in message.mentions and member != message.author:
                    c += 1

                if member == message.author and len(message.mentions) >= 1 :
                    if member not in message.mentions:
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

async def createLBEm(ctx):
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

async def updateLB(ctx):
    config = getConfig(ctx)
    lb_channelid = int(config["LB"]["Channel ID"])
    lb_messageid = int(config["LB"]["Message ID"])

    if lb_channelid != 0 and lb_messageid != 0:
        print('Updating Leaderboard...')

        channel = bot.get_channel(lb_channelid)
        lbmessage = await channel.fetch_message(lb_messageid)
       
        em = await createLBEm()
        await lbmessage.edit(embed=em)
        print('Leaderboard Updated!')

    else:
        print('Leaderboard not Initialized!')

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
async def on_message(message):
    # Get Message Context
    ctx = bot.get_context(message)

    # Retrieve Config
    config = getConfig(ctx)
    guild_info = getGuildInfo(ctx)

    # Retrieve Messages if no quotes in messages attribute in Guild Info
    if len(guild_info.messages) == 0:
        getQuotes(ctx)

    if not message.author.bot:
        print(f'[{message.guild}] ({message.channel}) {message.author}: {message.content}')

    if message.content.startswith("q."):
        print("Command Detected!")

        await bot.process_commands(message)
        return
    
    if message.content == "yo":
        print(f"{message.content}\noye")
        ctx = await bot.get_context(message)
        await ctx.send("oye")

        await bot.process_commands(message)
        return

    if message.channel.id == config["Q Channel"]:
        guild_info.messages.append(message)
        if len(message.mentions) > 0:
            await count(ctx)
            await updateLB(ctx)

    await bot.process_commands(message)
    return

# --------------------------------- Bot Commands ----------------------------------
# Get a random quote from the server
@bot.command()
async def random(ctx):
    print("Getting a random quote...")
    # Get List of Quotes for Guild
    data = getGuildInfo(ctx)
    messages = data.messages

    # Choose a quote
    message = rand.choice(messages)
    quote = str(message.content)

    # Replace User IDs with username
    for mentioned in message.mentions:
        quote = quote.replace(f'<@!{mentioned.id}>', f'@{mentioned.name}').replace(f'<@{mentioned.id}>', f'@{mentioned.name}')
    print('Got a Random Quote!')

    # Get Link to original quote
    print(f'discordapp.com/channels/{data.id}/{os.getenv("qChannelID")}/{message.id}')

    # Prepare the Embed
    print('Preparing Embed...')
    em = dc.Embed(title='Your Random Quote:', color=0xffbf00, url=f'https://discord.com/channels/{data.id}/{os.getenv("qChannelID")}/{message.id}')
    em.add_field(name=quote, value = "")

    att_ems = []
    att_ems.append(em)

    # if len(message.attachments) != 0:
    for attachment in message.attachments:
        att = dc.Embed()
        att.set_image(url = attachment.url)
        att_ems.append(att)

    em.set_footer(text='Truly Words of Wisdom...')
    print('Sending Random Quote Embed!')

    await ctx.send(embed = att_ems)

# Retrieve Quotes of Specified User
@bot.command()
async def quotes(ctx):
    user = []
    user = ctx.message.mentions

    if len(user) != 1:
        await ctx.send('Invalid Number of Users...\n**Usage:** q.quotes @user')
        return
    else:
        await getMentions(ctx, user[0])
        dump_path = f'./data/{ctx.guild}/dump.txt'
        await ctx.message.author.send(f"Here are the quotes of {user[0]}: ", file=dc.File(dump_path))

# Retrieve Quotes Authored by Specified User
@bot.command()
async def authour(ctx):
    user = []
    user = ctx.message.mentions

    if len(user) != 1:
        await ctx.send('Invalid Number of Users...\n**Usage:** q.authour @user')
        return
    else:
        await getAuthoured(ctx, user[0])
        dump_path = f'./data/{ctx.guild}/dump.txt'
        await ctx.message.author.send(f"Here are the quotes authored by {user[0]}: ", file=dc.File(dump_path))

# For people from the USA
@bot.command()
async def author(ctx):
    await authour(ctx)

# Funny Joke Command
@bot.command()
async def bingchilling(ctx):
  await ctx.send("早上好中國現在我有冰淇淋")

# -------------------------------- Admin Commands ---------------------------------
# Command to set q channel
# Usage: q.setQChannel [channel ID]
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

# Command to initialize leaderboard
# Usage: q.initLB
@bot.command()
@comms.has_permissions(administrator=True)
async def initLB(ctx):
    em = await createLBEm()
    lb = await ctx.send(embed=em)
    config = getConfig(ctx)
    lbobj = {
        "Channel ID" : int(lb.get_channel().id),
        "Message ID" : int(lb.id)
    }

    editConfig(ctx, config, "LB", lbobj)

    await ctx.send(embed=em)

@bot.command()
@comms.has_guild_permissions(administrator=True)
async def refresh(ctx):
    print(f"Refreshing Leaderboard for {ctx.guild.name} Manually...")
    await getQuotes(ctx)
    await count(ctx)
    await updateLB(ctx)
    print("Leaderboard Manually Refreshed!")

bot.remove_command('help')
bot.run(os.getenv('TOKEN'))