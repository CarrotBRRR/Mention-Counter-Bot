import os, json
import operator as op
import random as rand
import discord as dc
from discord.ext import commands as comman
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()

# Setting JSON Filename
filepath = os.getenv('filepath')
txtdump = os.getenv('txtdump')

# Setting Intents
intents = dc.Intents.default()
intents.message_content = True
intents.members = True
bot = comman.Bot(command_prefix="q.", intents=intents)
guildID = os.getenv('guildID')

# Get all message history and returns an array of 
# all messages of hardcoded channel
# Needs Context to access quote channel
async def getMessages(ctx):
  print('Retrieving Message history...')
  channel = dc.utils.get(ctx.guild.channels, name=os.getenv('quoteChannel'))
  global messages
  messages = []
  async for message in channel.history(limit=None):
    messages.append(message)
  messages.reverse()
  print('Messages retrieved!')
  return messages

# Counts number of times mentioned in a channel
# Needs to pass a message event to access the guild
async def count(message):
  data = []
  guild = message.channel.guild

  print('Beginning Count...')

  for member in guild.members:
    if not member.bot:
      c = 0
      a = 0
      for message in messages:
        if member in message.mentions:
          c += 1
        if member == message.author and len(message.mentions) >= 1:
          a += 1

      if c > 0:
        obj = {
            "Name": str(member.name),
            "Mentions": int(c),
            "Authored": int(a)
        }
        data.append(obj)

  print('Finished Counting for All Members!')
  data.sort(key=op.itemgetter('Mentions'), reverse=True)

  with open(filepath, 'w', encoding="utf-8") as f:
    json.dump(data, f, indent=4)
    
  print('Data refreshed!')
  return data

#Gets the scores from a JSON
async def getScores():
  print('Getting Scores...')
  with open(filepath, 'r') as f:
    members = json.load(f)

  userList = []
  for user in members:
    Name = user["Name"]
    Count = int(user["Mentions"])
    Authored = int(user["Authored"])
    userList.append([Name, Count, Authored])

  print('Scores Retrieved!')

  return userList

# Get all quotes of a specified member
# Needs specified member and context to 
async def getMentions(member, ctx):
  quotes = ""
  quote = ""
  channel = dc.utils.get(ctx.guild.channels, name=os.getenv('quoteChannel'))
  print(f'Searching for mentions of {member.name} in {channel}...')
  for message in messages:
    if member in message.mentions:
      quote = str(message.content)
      for mentioned in message.mentions:
        quote = quote.replace(f'<@!{mentioned.id}>', f'@{mentioned.name}').replace(f'<@{mentioned.id}>', f'@{mentioned.name}')

      quotes += quote + "\n\n"
  print('All mentions Found!')
  with open(txtdump, 'w', encoding='utf-8') as f:
    f.write(quotes)

async def getAuthor(member, ctx):
  quotes = ""
  quote = ""
  channel = dc.utils.get(ctx.guild.channels, name=os.getenv('quoteChannel'))
  print(f'Searching for Author {member.name} in {channel}...')
  for message in messages:
    if member == message.author and len(message.mentions) >= 1:
      quote = str(message.content)
      for mentioned in message.mentions:
        quote = quote.replace(f'<@!{mentioned.id}>', f'@{mentioned.name}').replace(f'<@{mentioned.id}>', f'@{mentioned.name}')

      quotes += quote + "\n\n"
  print(f'All quotes with author {member.name} Found!')
  with open(txtdump, 'w', encoding='utf-8') as f:
    f.write(quotes)

#Easter Egg
async def getLuddy(ctx):
  print("Fetching the Luddy quotes...")
  IDs = [834631585596309515, 793018805239808030, 728870835170967593, 720528612167778365]
  quotes = ""
  channel = dc.utils.get(ctx.guild.channels, name=os.getenv('quoteChannel'))
  for ID in IDs:
    message = await channel.fetch_message(ID)
    quotes += message.content.replace("<@!336001822177099776>", "@LuddyLion").replace("<@336001822177099776>", "@LuddyLion") + "\n\n"

  quotes
  print('The Luddy Quotes have been Fetched!')
  with open(txtdump, 'w', encoding='utf-8') as f:
    f.write(quotes)

#Get a random message from the quotes channel
async def getRandom():
  print("Getting a random quote...")

  message = rand.choice(messages)
  quote = str(message.content)

  for mentioned in message.mentions:
    quote = quote.replace(f'<@!{mentioned.id}>', f'@{mentioned.name}').replace(f'<@{mentioned.id}>', f'@{mentioned.name}')
  print('Got a Random Quote!')

  return quote

async def editLB(message):
  print('Editing Leaderboard...')
  channel = bot.get_channel(int(os.getenv('LBChannelID')))
  print(channel)
  lb = await channel.fetch_message(int(os.getenv('LBMessageID')))

  em = await createLBEmbed()
  await lb.edit(embed=em)
  print('Leaderboard Edited!')

async def createLBEmbed():
  list = await getScores()
  index = 1

  em = dc.Embed(title='Most Quoted Members:', color=0xffbf00)
  for user in list:
    em.add_field(name=f'{index}. {list[index-1][0]}',
                  value=f'{list[index-1][1]} Quotes',
                  inline=False)
    index += 1
  em.set_footer(text="Brought to you by: CarrotBRRR")

  return em

@bot.event
async def on_message(message):
  if 'messages' not in globals():
    await getMessages(message)
    await count(message)

  print(f'({message.channel}) {message.author}: {message.content}')
  
  if message.author.bot:
    print('Message is from bot')

    await bot.process_commands(message)
    return

  if message.content.startswith("q."):
    print(f'Message is a Command ({message.content})')

    await bot.process_commands(message)
    return

  if message.content == "yo":
    print(f"{message.content}\noye")
    ctx = await bot.get_context(message)
    await ctx.send("oye")

    await bot.process_commands(message)
    return

  else:
    if str(message.channel) == os.getenv('quoteChannel'):
      messages.append(message)
      if len(message.mentions) > 0:
        await count(message)
        await editLB(message)

  await bot.process_commands(message)
  return

#Send a message to Console when Bot is Ready
@bot.event
async def on_ready():
  print(f'Bot connected as {bot.user}')

#Funny Joke Command
@bot.command()
async def bingchilling(ctx):
  await ctx.send("早上好中國現在我有冰淇淋")

@bot.command()
async def changedaworld(ctx):
  print('getting the Legendary quote')
  channel = dc.utils.get(ctx.guild.channels, name=os.getenv('quoteChannel'))
  message = await channel.fetch_message(889736462038335538)
  embedarray = []
  em = dc.Embed(title='The Most Legendary Quote', color=0xffbf00)
  for item in message.attachments:
    link = item.url
    em.set_image(url=link)
    embedarray.append(em)
  print('Legendary Quote Retrieved!')
  em.add_field(name=message.content, value ="")
  await ctx.send(embeds=embedarray)

#Initiallizes Leaderboard Location
@bot.command()
async def init(ctx):
  print('Initializing Leaderboard...')
  await count(ctx)
  print('Leaderboard Initialized for Channel \"' + str(ctx.channel) + '\"!')

#retrieves scores and sends an embedded leaderboard
@bot.command()
async def leaderboard(ctx):
  em = await createLBEmbed()
  await ctx.send(embed=em)

@bot.command()
async def random(ctx):
  print("Getting a random quote...")
  message = rand.choice(messages)
  quote = str(message.content)

  for mentioned in message.mentions:
    quote = quote.replace(f'<@!{mentioned.id}>', f'@{mentioned.name}').replace(f'<@{mentioned.id}>', f'@{mentioned.name}')
  print('Got a Random Quote!')

  print(f'discordapp.com/channels/{guildID}/{os.getenv("qChannelID")}/{message.id}')

  print('Preparing Embed...')
  em = dc.Embed(title='Your Random Quote:', color=0xffbf00, url=f'https://discord.com/channels/{guildID}/{os.getenv("qChannelID")}/{message.id}')
  em.add_field(name=quote, value = "")
  if len(message.attachments) != 0:
    em.set_image(url=message.attachments[0].url)
  em.set_footer(text='Truly Words of Wisdom...')
  print('Sending Random Quote Embed!')

  await ctx.send(embed = em)

@bot.command()
async def quotes(ctx):
  user = []
  user = ctx.message.mentions

  if len(user) != 1:
    if ctx.message.content.endswith('LuddyLion'):
      print("Someone requested the Luddy Lion")
      await getLuddy(ctx)
      await ctx.message.author.send(f"Here is the quotes of The Luddy Lion: ", file=dc.File(txtdump))
      return

    if ctx.message.content.endswith('Gay'):
      rand = await getRandom()
      await ctx.message.author.send(rand)

    else:
      await ctx.send('Invalid Number of Users...')
      return

  else:
    await getMentions(user[0], ctx)
    await ctx.message.author.send(f"Here is the quotes of {user[0]}: ", file=dc.File(txtdump))

@bot.command()
async def author(ctx):
  user = []
  user = ctx.message.mentions
  if len(user) != 1:
    await ctx.send('Invalid Number of Users...')
    return
  else:
    await getAuthor(user[0], ctx)
    await ctx.message.author.send(f"Here is the quotes authored by {user[0]}: ", file=dc.File(txtdump))

@bot.command()
async def authour(ctx):
  await author(ctx)

@bot.command()
async def commands(ctx):
  em = dc.Embed(title="Command List:")
  em.add_field(name='q.quotes @user', value='Retrieves and Sends all quotes attributed to @user')
  em.add_field(name='q.random', value='Chooses a random message in quotes channel and sends it')
  em.set_footer(text='Brought to you by: CarrotBRRR')
  await ctx.send(embed=em)
  await ctx.message.author.send('**Keep this a secret...**\n(Headphone warning)', 
                                file=dc.File(os.getenv('audiopath')))
  
@bot.command()
async def refresh(ctx):
  print("Refreshing Message Database Manually...")
  await getMessages(ctx)
  await count(ctx)
  print("Message Database Manually Refreshed!")
  await ctx.send("**Message Database Manually Refreshed!**")

@bot.command()
async def updateLB(ctx):
  print("Refreshing Leaderboard Manually...")
  await getMessages(ctx)
  await count(ctx)
  await editLB(ctx)
  print("Leaderboard Manually Refreshed!")
  await ctx.send("**Leaderboard Manually Refreshed!**")
  
bot.remove_command('help')
bot.run(os.getenv('TOKEN'))
