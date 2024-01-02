import os, json
import operator as op
import random as rand
import discord as dc
import typing

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

# ----------------------------------- Functions -----------------------------------
# Retrieves config for ctx
async def getConfig(ctx):
    filepath = f'./data/{ctx.guild.id}/ServerInfo.json'

    with open(filepath, 'r') as f:
        config = json.load(f)

    return config

# Edits the given config, attribute to change 
# and newdata to change
async def editConfig(ctx, config, attribute, newdata):
    filepath = f'./data/{ctx.guild.id}/ServerInfo.json'
    config[attribute] = newdata

    with open(filepath, 'w+') as f:
        json.dump(config, f, indent=4)

    return 0

# Retrieves GuildInfo Class object with matching ID
# Creates a new GuildInfo if not found
async def getGuildInfo(ctx):
    for data in guilds:
        if data.id == ctx.guild.id:
            return data
    
    print('Could not find Guild Data, Creating...')
    data = GuildInfo(ctx.guild.name, ctx.guild.id)
    guilds.append(data)
    print('Created!')
    return data

# Retrieves Messages from Quotes Channel and stores it in 
# the messages attribute of GuildInfo class object
async def getQuotes(ctx):
    data = await getGuildInfo(ctx)
    config = await getConfig(ctx)
    channel = dc.utils.get(ctx.guild.channels, id=config["Q Channel"])
    messages = []
    print(f'Retrieving Quotes for {ctx.guild} in {channel.name}')
    async for message in channel.history(limit=None):
        messages.append(message)
    messages.reverse()

    data.setMessages(messages)

    print('Quotes Retrieved!')

# Retrieves Messages from Specified Channel and 
# stores it in a temporary global buffer
async def getMessageHistory(ctx, channel):
    message_buffer = []

    async for message in channel.history(limit=None):
        message_buffer.append(message)

    return message_buffer

# Retrieves Messages that Mention the specified user
async def getMentions(ctx, member):
    quote = ""
    quotes = ""

    data = await getGuildInfo(ctx)

    print(f'Searching for mentions of {member.name} in cache of {ctx.guild}...')

    for message in data.messages:
        if member in message.mentions:
            quote = str(message.content)
            for mentioned in message.mentions:
                quote = quote.replace(f'<@!{mentioned.id}>', f'@{mentioned.name}').replace(f'<@{mentioned.id}>', f'@{mentioned.name}')
            
            quotes += quote + "\n\n"

    print('All mentions Found!')
    
    with open(f'./data/{ctx.guild.id}/dump.txt', 'w+', encoding='utf-8') as d:
        d.write(quotes)

async def getAuthoured(ctx, member):
    quote = ""
    quotes = ""
    
    data = await getGuildInfo(ctx)

    print(f'Searching for Author {member.name} in cache of {ctx.guild}...')

    for message in data.messages:
        if member == message.author and len(message.mentions) >= 1:
            quote = str(message.content)
            for mentioned in message.mentions:
                quote = quote.replace(f'<@!{mentioned.id}>', f'@{mentioned.name}').replace(f'<@{mentioned.id}>', f'@{mentioned.name}')
            
            quotes += quote + "\n\n"

    print(f'All quotes by author {member.name} Found!')

    with open(f'./data/{ctx.guild.id}/dump.txt', 'w+', encoding='utf-8') as f:
        f.write(quotes)

# Counts amount of times mentioned in
# the cached messages in GuildInfo class object
async def count(ctx):
    guild_info = await getGuildInfo(ctx)
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
    filepath = f'./data/{ctx.guild.id}/Leaderboard.json'

    counts.sort(key=op.itemgetter('Mentions'), reverse=True)

    with open(filepath, 'w+', encoding="utf-8") as f:
        json.dump(counts, f, indent=4)

    print('Scores Saved!')
    return counts

# Retrieves scores from the Leaderboard.json
async def getScores(ctx):
    print('Getting Scores...')
    # Load JSON containing Scores
    filepath = f'./data/{ctx.guild.id}/Leaderboard.json'

    with open(filepath, 'r') as f:
        users = json.load(f)

    # Initialize Scores Array
    Scores = []

    for user in users:
        # Extract Data from JSON
        score = {
                "Name": user["Name"],
                "Mentions": int(user["Mentions"]),
                "Authored": int(user["Authored"])
            }

        Scores.append(score)

    print('Scores Retrieved!')
    
    return Scores

async def createLBEm(ctx):
    scores = await getScores(ctx)
    index = 1

    em = dc.Embed(title='Most Quoted Members:', color=0xffbf00)
    for user in scores:
        em.add_field(name=f'{index}. {user["Name"]}',
                        value=f'> {user["Mentions"]} Quotes\n> {user["Authored"]} Authored',
                        inline=False)
        index += 1
    em.set_footer(text="Brought to you by: CarrotBRRR")

    return em

async def updateLB(ctx):
    config = await getConfig(ctx)
    lb_channelid = int(config["LB"]["Channel ID"])
    lb_messageid = int(config["LB"]["Message ID"])

    if lb_channelid != 0 and lb_messageid != 0:
        print('Updating Leaderboard...')

        channel = bot.get_channel(lb_channelid)
        lbmessage = await channel.fetch_message(lb_messageid)
       
        em = await createLBEm(ctx)
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
    global guilds
    guilds = []

    for guild in bot.guilds:

        # Create a GuildInfo Class Object
        data = GuildInfo(guild.name, guild.id)
        guilds.append(data)

        # Get Path for specific guild
        filepath = f'./data/{guild.id}'

        # Set-up Directory and Config
        if not os.path.exists(filepath):
            print(f'Setting up Directory for {guild.name}...')
            os.mkdir(filepath)

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
            with open(f'{filepath}/ServerInfo.json', 'w+') as f:
                json.dump(info, f, indent=4)
                
            print(f'Directory for {guild.name} initialized!')
    print('Files Initialized!')
    print(f'Bot connected as {bot.user}')

@bot.event
async def on_guild_join(guild):
    data = GuildInfo(guild.name, guild.id)
    guilds.append(data)

    # Get Path for specific guild
    filepath = f'./data/{guild.id}'

    # Set-up Directory and Config
    if not os.path.exists(filepath):
        print(f'Setting up Directory for {guild.name}...')
        os.mkdir(filepath)

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
        with open(f'{filepath}/ServerInfo.json', 'w+') as f:
            json.dump(info, f, indent=4)
            
        print(f'Directory for {guild.name} initialized!')

@bot.event
async def on_interaction(interaction):
    if interaction.guild is not None:
        # Retrieve Config
        ctx = await bot.get_context(interaction)
        config = await getConfig(ctx)
        guild_info = await getGuildInfo(ctx)

        if config["Q Channel"] != 0 and not guild_info.hasMessages():
            await getQuotes(ctx)

@bot.event
async def on_message(message):
    if not message.author.bot:
        print(f'[{message.guild}] ({message.channel}) {message.author}:\n   {message.content}')

    ctx = await bot.get_context(message)
    if ctx.guild is not None:
        # Retrieve Config
        try:
            config = await getConfig(ctx)
        except FileNotFoundError:
            print("Directory not initialized.")
            return
        
        guild_info = await getGuildInfo(ctx)

        # Retrieve Messages if no quotes in messages attribute in Guild Info
        if config["Q Channel"] != 0 and not guild_info.hasMessages():
            await getQuotes(ctx)

        if message.channel.id == config["Q Channel"]:
            guild_info.messages.append(message)

            if len(message.mentions) > 0:
                await count(ctx)
                await updateLB(ctx)
        
    if message.content == "yo":
        print(f"oye")
        ctx = await bot.get_context(message)
        await ctx.send("oye")

    if message.content == "git add -A":
        ctx = await bot.get_context(message)
        await ctx.send("If you didn't mean to send this here, take a break from coding lmfao\n~Dom")

    await bot.process_commands(message)
    return

@bot.event
async def on_message_edit(m_before, m_after):
    if not m_before.author.bot:
        print(f'[{m_before.guild}] ({m_before.channel}) {m_before.author} edited:\n   {m_before.content}\n   -> {m_after.content}')

# --------------------------------- Bot Commands ----------------------------------
# Get a random quote from the server
@bot.hybrid_command(
    name="random",
    description="Get a random quote from the quote channel!"
)
async def random(ctx, channel: typing.Optional[dc.TextChannel]=None):
    if channel is None:
        print("Getting a random quote from Quote Channel...")
        
        # Get List of Quotes for Guild
        data = await getGuildInfo(ctx)
        messages = data.messages

    elif channel is not None:
        print(f'Getting a random quote from {channel}')
        messages = await getMessageHistory(ctx, channel)

    else:
        print('An unexpected error occured...')
        return

    # Choose a quote
    message = rand.choice(messages)
    quote = str(message.content)

    # Replace User IDs with username
    for mentioned in message.mentions:
        quote = quote.replace(f'<@!{mentioned.id}>', f'@{mentioned.name}').replace(f'<@{mentioned.id}>', f'@{mentioned.name}')

    print('Got a Random Quote!')

    # Get Link to original quote
    print(f'discordapp.com/channels/{message.guild.id}/{message.channel.id}/{message.id}')

    # Prepare the Embed
    print('Preparing Embed...')
    em = dc.Embed(title='Your Random Quote:', color=0xffbf00, 
                url=f'https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}')
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

    await ctx.send(embeds=att_ems)

# Retrieve Quotes of Specified User
@bot.hybrid_command(
    name="quotes",
    description="Get all quotes from @user. Usage: /quotes @user"
)
async def quotes(ctx):
    user = []
    user = ctx.message.mentions

    if len(user) != 1:
        await ctx.send('Invalid Number of Users...\n**Usage:** q.quotes @user')
        return
    
    else:
        await getMentions(ctx, user[0])
        dump_path = f'./data/{ctx.guild.id}/dump.txt'
        await ctx.message.author.send(f"Here are the quotes of {user[0]}: ", file=dc.File(dump_path))

# Retrieve Quotes Authored by Specified User
@bot.hybrid_command(
    name="authour",
    description="Get all quotes authoured by @user. Usage: /authour @user"
)
async def authour(ctx):
    user = []
    user = ctx.message.mentions

    if len(user) != 1:
        await ctx.send('Invalid Number of Users...\n**Usage:** q.authour @user')
        return
    
    else:
        await getAuthoured(ctx, user[0])
        dump_path = f'./data/{ctx.guild.id}/dump.txt'
        await ctx.message.author.send(f"Here are the quotes authored by {user[0]}: ", file=dc.File(dump_path))

# For people from the USA
@bot.hybrid_command(
    name="author",
    description="Same as /authour, but for people from the USA"
)
async def author(ctx):
    await authour(ctx)

# Make the bot say something
# Usage: q.say #channel #channel2 "message"
@bot.command()
async def say(ctx, channel, *args):
    sayload = ' '.join(args)

    channel = channel.strip('<#').strip('>')
    ch = bot.get_channel(int(channel))

    await ch.send(f'{sayload}')

# Funny Joke Command
@bot.command()
async def bingchilling(ctx):
  await ctx.send("早上好中國現在我有冰淇淋")

# -------------------------------- Admin Commands ---------------------------------
# Command to set q channel
# Usage: q.setQChannel #channel
@bot.hybrid_command(
    name="setqchannel",
    description="(Admin Only) Set the channel to a specified #channel"
)
@comms.has_permissions(administrator=True)
async def setQChannel(ctx):
    if len(ctx.message.channel_mentions) == 1:
        print("Setting up default channel...")

        config = await getConfig(ctx)
        await editConfig(ctx, config, "Q Channel", ctx.message.raw_channel_mentions[0])

        channel = bot.get_channel(config["Q Channel"])

        print(f'Q Channel for {ctx.guild.name} is now {channel}')

    else: 
        ctx.send("invalid number of channels")
        print("invalid number of channels")

# Command to initialize leaderboard
# Usage: q.initLB
@bot.hybrid_command(
    name="initlb",
    description="(Admin Only) Create or Overwrite the Leaderboard"
)
@comms.has_permissions(administrator=True)
async def initLB(ctx):
    await getQuotes(ctx)
    await count(ctx)

    config = await getConfig(ctx)
    em = await createLBEm(ctx)
    lb = await ctx.send(embed=em)

    lbobj = {
        "Channel ID" : int(lb.channel.id),
        "Message ID" : int(lb.id)
    }

    await editConfig(ctx, config, "LB", lbobj)

@bot.hybrid_command(
    name="refresh",
    description="(Admin Only) Manually Refresh the Leaderboard and Scores"
)
@comms.has_guild_permissions(administrator=True)
async def refresh(ctx):
    print(f"Refreshing Leaderboard for {ctx.guild.name} Manually...")

    await getQuotes(ctx)
    await count(ctx)
    await updateLB(ctx)

    print("Leaderboard Manually Refreshed!")


# -------------------------------- Owner Commands ---------------------------------
@bot.command(description="Initialize stack data")
@comms.is_owner()
async def start(ctx):
    ctx.send("This command currently does nothing.")

@bot.command(description="Turns off bot (bat restart)")
@comms.is_owner()
async def stop(ctx: comms.Context):
    print("Shutting down...")
    await bot.close()
    print("Goodbye!")


@bot.command(description="sync all global commands")
@comms.is_owner()
async def sync(ctx: comms.Context):
    print("Sycning tree...")
    await bot.tree.sync()
    print("Synced")

@bot.command(description="initialize database for all guilds on startup")
@comms.is_owner()
async def go(ctx: comms.Context):
    for guild in bot.guilds:
        for data in guilds:
            if data.id == guild.id:
                    filepath = f'./data/{guild.id}/ServerInfo.json'
                    with open(filepath, 'r') as f:
                        config = json.load(f)

                    if config["Q Channel"] != 0:
                        channel = dc.utils.get(guild.channels, id=config["Q Channel"])
                        messages = []

                        print(f'Retrieving Quotes for {guild} in {channel.name}')
                        if channel is not None:
                            async for message in channel.history(limit=None):
                                messages.append(message)
                            messages.reverse()

                            data.setMessages(messages)
                        else:
                            continue
                    else:
                        continue

bot.remove_command('help')
bot.run(os.getenv('TOKEN'))