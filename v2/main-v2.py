import os, json, sys
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
sys.stdout.reconfigure(encoding='utf-8')

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
    
    print(f'[INFO] Could not find Guild Data, Creating...')
    data = GuildInfo(ctx.guild.name, ctx.guild.id)
    guilds.append(data)
    print(f'[INFO] Created!')
    return data

# Retrieves Messages from Quotes Channel and stores it in 
# the messages attribute of GuildInfo class object
async def getQuotes(ctx):
    data = await getGuildInfo(ctx)
    config = await getConfig(ctx)
    channel = dc.utils.get(ctx.guild.channels, id=config["Q Channel"])
    messages = []
    print(f'[INFO] Retrieving Quotes for {ctx.guild} in {channel.name}')
    async for message in channel.history(limit=None):
        messages.append(message)
    messages.reverse()

    data.setMessages(messages)

    print(f'[INFO] Quotes Retrieved!')

# Retrieves Messages from Specified Channel and 
# stores it in a temporary global buffer
async def getMessageHistory(ctx, channel):
    if 'prev_channelid' not in globals():
        global prev_channelid
        global message_buffer
        prev_channelid = None
    
    if channel.id != prev_channelid or prev_channelid is None:
        message_buffer = []

        async for message in channel.history(limit=None):
            message_buffer.append(message)

    prev_channelid = channel.id
    return message_buffer

# Retrieves Messages that Mention the specified user
async def getMentions(ctx, member):
    quote = ""
    quotes = ""

    data = await getGuildInfo(ctx)

    print(f'[INFO] Searching for mentions of {member.name} in cache of {ctx.guild}...')

    for message in data.messages:
        if member in message.mentions:
            quote = str(message.content)
            for mentioned in message.mentions:
                quote = quote.replace(f'<@!{mentioned.id}>', f'@{mentioned.name}').replace(f'<@{mentioned.id}>', f'@{mentioned.name}')
            
            quotes += quote + "\n\n"

    print(f'[INFO] All mentions found!')
    
    with open(f'./data/{ctx.guild.id}/messages.txt', 'w+', encoding='utf-8') as d:
        d.write(quotes)

# Retrieves Messages that Mention a user and 
# are Authored by the specified user
async def getAuthored(ctx, member):
    quote = ""
    quotes = ""
    
    data = await getGuildInfo(ctx)

    print(f'[INFO] Searching for Author {member.name} in cache of {ctx.guild}...')

    for message in data.messages:
        if member == message.author and len(message.mentions) >= 1:
            quote = str(message.content)
            for mentioned in message.mentions:
                quote = quote.replace(f'<@!{mentioned.id}>', f'@{mentioned.name}').replace(f'<@{mentioned.id}>', f'@{mentioned.name}')
            
            quotes += quote + "\n\n"

    print(f'[INFO] All quotes by author {member.name} found!')

    with open(f'./data/{ctx.guild.id}/messages.txt', 'w+', encoding='utf-8') as f:
        f.write(quotes)

# Counts amount of times mentioned in
# the cached messages in GuildInfo class object
async def count(ctx):
    guild_info = await getGuildInfo(ctx)
    counts = []

    print(f'[INFO] Beginning Quote Count for {ctx.guild.name}...')
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

    filepath = f'./data/{ctx.guild.id}/Leaderboard.json'
    counts.sort(key=op.itemgetter('Mentions'), reverse=True)
    with open(filepath, 'w+', encoding="utf-8") as f:
        json.dump(counts, f, indent=4)

    print(f'[INFO] Scores Saved!')
    return counts

# Retrieves scores from the Leaderboard.json
async def getScores(ctx):
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

    print(f'[INFO] Scores Retrieved!')
    
    return Scores

# Create the Leaderboard based on the stored leaderboard
async def createLBEm(ctx):
    scores = await getScores(ctx)
    ems = []
    em = dc.Embed(title='Most Quoted Members:', color=0xffbf00)
    em.set_footer(text='Page 1')
    page_number = 1
    for i, user in enumerate(scores):
        em.add_field(
            name=f'{i + 1}. {user["Name"]}',
            value=f'> {user["Mentions"]} Quotes\n> {user["Authored"]} Authored',
            inline=False
        )

        # Start a new embed every 25 fields
        if i % 25 == 24:
            page_number += 1
            ems.append(em)
            em = dc.Embed(title=f'', color=0xffbf00)
            em.set_footer(text=f'Page {page_number}')


    ems.append(em)

    # Set footer on the last embed
    if ems:
        ems[-1].set_footer(text=f'Page {page_number}\n----------------------------\nBrought to you by CarrotBRRR')

    return ems

# Edits the Leaderboard with updated data
async def updateLB(ctx):
    config = await getConfig(ctx)
    lb_channelid = int(config["LB"]["Channel ID"])
    lb_messageid = int(config["LB"]["Message ID"])

    if lb_channelid != 0 and lb_messageid != 0:
        print(f'[INFO] Updating Leaderboard...')

        channel = bot.get_channel(lb_channelid)
        lbmessage = await channel.fetch_message(lb_messageid)
       
        ems = await createLBEm(ctx)
        await lbmessage.edit(embeds=ems)
        print(f'[INFO] Leaderboard Updated!')

    else:
        print(f'[ERROR] Leaderboard not Initialized!')

# ----------------------------------- Bot Events ----------------------------------
@bot.event
async def on_ready():
    if not os.path.exists("./logs"):
        os.mkdir('./logs')

    print(f'[INFO] Initializing Files...')
    
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
            print(f'[INFO] Setting up Directory for {guild.name}...')
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
                
            print(f'[INFO] Directory for {guild.name} initialized!')
    print(f'[INFO] Files Initialized!')
    print(f'[INFO] Bot connected as {bot.user}')

@bot.event
async def on_guild_join(guild):
    data = GuildInfo(guild.name, guild.id)
    guilds.append(data)

    # Get Path for specific guild
    filepath = f'./data/{guild.id}'

    # Set-up Directory and Config
    if not os.path.exists(filepath):
        print(f'[INFO] Setting up Directory for {guild.name}...')
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
            
        print(f'[INFO] Directory for {guild.name} initialized!')

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
        text = str(message.content).replace("\n","\n\t")
        print(f'+ [{message.guild}] ({message.channel}) {message.author}:\n\t{text}')

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
        await ctx.send("If you didn't mean to send that here, take a break from coding lmfao\n~Dom")

    await bot.process_commands(message)
    return

@bot.event
async def on_message_edit(m_before, m_after):
    if not m_before.author.bot:
        before_text = str(m_before.content).replace("\n","\n\t")
        after_text = str(m_after.content).replace("\n","\n\t")

        print(f'* [{m_before.guild}] ({m_before.channel}) {m_before.author} Edited:\n\t   {before_text}\n   -> {after_text}')

@bot.event
async def on_message_delete(message):
    if not message.author.bot:
        text = str(message.content).replace("\n","\n\t")

        print(f'- [{message.guild}] ({message.channel}) Message by {message.author} Deleted:\n   {text}\n')

# --------------------------------- Bot Commands ----------------------------------
# Get a random quote from the server
@bot.hybrid_command(
    name="random",
    description="Get a random quote from the quote channel!"
)
async def random(ctx, channel: typing.Optional[dc.TextChannel]=None):
    if channel is None:
        print(f'[INFO] Getting a random quote from Quote Channel...')
        m = await ctx.send(f'Getting a random quote from Quote Channel...')
        # Get List of Quotes for Guild
        data = await getGuildInfo(ctx)
        messages = data.messages

    elif channel is not None:
        print(f'[INFO] Getting a random quote from {channel}')
        m = await ctx.send(f'Getting a random quote from {channel}...')
        messages = await getMessageHistory(ctx, channel)

    # Choose a quote
    message = rand.choice(messages)
    
    # Prepare the Embed
    em = dc.Embed(title='Your Random Message:', color=0xffbf00, 
                url=f'https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}')
    em.add_field(name="", value=message.content)

    em.set_footer(text='Truly Words of Wisdom...')

    att_ems = []
    att_ems.append(em)

    # if len(message.attachments) != 0:
    for attachment in message.attachments:
        att = dc.Embed()
        att.set_image(url = attachment.url)
        att_ems.append(att)

    if len(att_ems) > 10:
        await m.edit(content=None, embeds=att_ems[:10])
        i = len(att_ems)
        while i > 0:
            i -= 10
            att_ems = att_ems[10:]
            if i > 10:
                await ctx.send(content=None, embeds=att_ems[:10])
            elif i > 0 and i <= 10:
                await ctx.send(content=None, embeds=att_ems)
    else:
        await m.edit(content=None, embeds=att_ems)

# Retrieve Quotes of Specified User
@bot.hybrid_command(
    name="quotes",
    description="Get all quotes from @user. Usage: /quotes @user"
)
async def quotes(ctx, user: dc.Member):

    if user is None:
        await ctx.send('Invalid Number of Users.\n**Usage:** q.quotes @user', ephemeral=True)
        return
    
    else:
        await getMentions(ctx, user)
        dump_path = f'./data/{ctx.guild.id}/messages.txt'
        await ctx.send(f'Quotes of {user.name} retrieved!\nPlease check your DMs.')
        await ctx.message.author.send(f"Here are the quotes of {user.name}: ", file=dc.File(dump_path))

# Retrieve Quotes Authored by Specified User
@bot.hybrid_command(
    name="author",
    description="Get all quotes authoured by @user. Usage: /author @user"
)
async def author(ctx, user: dc.Member):
    if user is None:
        await ctx.send('Invalid Number of Users.\n**Usage:** q.author @user', ephemeral=True)
        return
    
    else:
        await getAuthored(ctx, user)
        dump_path = f'./data/{ctx.guild.id}/messages.txt'
        await ctx.send(f'Quotes by author {user.name} retrieved!\nPlease check your DMs.')
        await ctx.message.author.send(f"Here are the quotes authored by {user.name}: ", file=dc.File(dump_path))

# For people who can't spell
@bot.hybrid_command(
    name="authour",
    description="Same as /author, but for people who can't spell"
)
async def authour(ctx, user: dc.Member):
    await author(ctx, user)

@bot.hybrid_command(
    name="rank",
    description="Get your rank in the leaderboard!"
)
async def rank(ctx, user: typing.Optional[dc.Member]=None):
    msg = await ctx.send(f'Getting your rank...')

    if user is None:
        member = ctx.author  
        
    else:
        member = user
    
    filepath = f'./data/{ctx.guild.id}/Leaderboard.json'

    em = dc.Embed(title=f"{member.name}'s Rank:", color=0xffbf00)
    with open(filepath, 'r') as f:
        leaderboard = json.load(f)
        for i, user_data in enumerate(leaderboard):
            if user_data["Name"] == member.name:
                rank = i + 1
                break
        else:
            rank = None

        em.add_field(name="Rank", value=f"{rank}", inline=False)
        em.add_field(name="Mentions", value=f"{user_data['Mentions']}", inline=False)
        em.add_field(name="Authored", value=f"{user_data['Authored']}", inline=False)
        em.set_thumbnail(url=member.display_avatar.url)

    await msg.edit(content=None, embed=em)

# Make the bot say something
# Usage: q.sayin #channel "message"
@bot.hybrid_command(
    name="sayin",
    description="Make the bot say something in specified channel!"
)
async def sayin(ctx, channel: dc.TextChannel, message: str):
    r = await ctx.send(f'Sending Message to {channel.mention}...', ephemeral=True)

    sayload = message.replace('\\n','\n')
    await channel.send(f'{sayload}')

    sayload = sayload.replace('\n', '\n\t')
    print(f'+ [{ctx.guild}] ({channel}) {ctx.message.author} (Anonymous):\n\t{sayload}')

    await r.edit(content=f'Message sent to {channel.mention}!', delete_after=2)

@bot.hybrid_command(
    name="say",
    description="Make the bot say something in current channel!"
)
async def say(ctx, message: str):
    await sayin(ctx, ctx.channel, message)

@bot.hybrid_command(
    name="get",
    description="Get a specific message given a Message ID!"
)
async def get(ctx, message_id: str):
    m = await ctx.send(f'Getting your requested message...')

    msgid = int(message_id)
    message = None
    for channel in ctx.guild.channels:
        try:
            message = await channel.fetch_message(msgid)
            break

        except Exception as e:
            message = None
            continue

    if message is None:
        await m.edit(content="Please Input a Valid Message ID", delete_after=2)
        return

    em = dc.Embed(title='Your Requested Message:', color=0xffbf00, 
                url=f'https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}')
    
    em.add_field(name="", value=message.content)

    att_ems = []
    att_ems.append(em)

    # if len(message.attachments) != 0:
    for attachment in message.attachments:
        att = dc.Embed()
        att.set_image(url = attachment.url)
        att_ems.append(att)

    if len(att_ems) > 10:
        await m.edit(content=None, embeds=att_ems[:10])
        i = len(att_ems)
        while i > 0:
            i -= 10
            att_ems = att_ems[10:]
            if i > 10:
                await ctx.send(content=None, embeds=att_ems[:10])
            elif i > 0 and i <= 10:
                await ctx.send(content=None, embeds=att_ems)
    else:
        await m.edit(content=None, embeds=att_ems)

@bot.command()
async def multi_say(ctx, *channels, message: str):
    for channel in channels:
        await say(ctx, channel, message)

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
async def setQChannel(ctx, qchannel: dc.TextChannel):
    if qchannel is not None:
        print(f'[INFO] Setting up default channel...')

        config = await getConfig(ctx)
        await editConfig(ctx, config, "Q Channel", qchannel.id)

        channel = bot.get_channel(config["Q Channel"])

        print(f'[INFO] Q Channel for {ctx.guild.name} is now {channel}')
        await ctx.send(f'{channel} has been set to be the quotes channel!', ephemeral=True)

    else: 
        await ctx.send("invalid number of channels")
        print(f'[ERROR] invalid number of channels')

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
    print(f'[INFO] Refreshing Leaderboard for {ctx.guild.name} Manually...')
    m = await ctx.send(f'Refreshing leaderboard...', ephemeral=True)

    await getQuotes(ctx)
    await count(ctx)
    await updateLB(ctx)

    print(f'[INFO] Leaderboard Manually Refreshed!')
    await m.edit(content=f'Leaderboard Refreshed!', delete_after=5)

# -------------------------------- Trust Commands ---------------------------------
@bot.command()
@comms.has_role(int(os.getenv("TRUSTROLEID")))
async def logs(ctx):
    most_recent_time = 0
    most_recent_file = None

    for log in os.scandir(f'./logs/'):
        mod_time = log.stat().st_mtime_ns

        if mod_time > most_recent_time:
            # update the most recent file and its modification time
            most_recent_file = log.name
            most_recent_time = mod_time

    if most_recent_file is not None:        
        await ctx.author.send(content="**Here are the logs:**", file=dc.File(f'./logs/{most_recent_file}'))

# -------------------------------- Owner Commands ---------------------------------
@bot.command(description="Manually Refresh the Leaderboard and Scores")
@comms.is_owner()
async def owner_refresh(ctx):
    print(f'[INFO] Refreshing Leaderboard for {ctx.guild.name} Manually...')
    m = await ctx.send(f'Refreshing leaderboard...', ephemeral=True)

    await getQuotes(ctx)
    await count(ctx)
    await updateLB(ctx)

    print(f'[INFO] Leaderboard Manually Refreshed!')
    await m.edit(content=f'Leaderboard Refreshed!', delete_after=5)
    await ctx.message.delete()

@bot.command(description="Initialize stack data")
@comms.is_owner()
async def start(ctx):
    ctx.send("This command currently does nothing.")

@bot.command(description="Turns off bot (bat restart)")
@comms.is_owner()
async def stop(ctx: comms.Context):
    print(f'[INFO] Shutting down...')
    await bot.close()

@bot.command(description="sync all global commands")
@comms.is_owner()
async def sync(ctx: comms.Context):
    print(f'[INFO] Sycning tree...')
    await bot.tree.sync()
    print(f'[INFO] Synced')

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
                    print(f'[INFO] Retrieving Quotes for {guild}')
                          
                    if channel is not None:
                        print(f'\tQuotes Channel: {channel.name}')

                        async for message in channel.history(limit=None):
                            messages.append(message)
                        messages.reverse()

                        data.setMessages(messages)
                        print('\tDone!')

                    else:
                        print(f'[ERROR] Could not find quotes channel')
                        continue
                else:
                    continue
    print(f'[INFO] Finished startup sequence!')

bot.remove_command('help')
bot.run(os.getenv('TOKEN'))