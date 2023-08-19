import os, json, operator
import random as rand
import discord as dc
from discord.ext import commands
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
bot = commands.Bot(command_prefix="q.", intents=intents)
guildID = os.getenv('guildID')


# Counts number of times mentioned in a channel,
# given the Context
# Warning: Highly inneficient
async def count(message, messages):
  data = []
  guild = message.channel.guild

  print('Beginning Count...')

  for member in guild.members:
    if not member.bot:
      c = 0
      print('Counting for user ' + str(member) + '...')
      for message in messages:
        if member in message.mentions:
          c += 1
      if c > 0:
        obj = {
            "Name": str(member.name),
            "Mentions": int(c)
        }
        data.append(obj)

  print('Finished Counting for All Members!')
  data.sort(key=operator.itemgetter('Mentions'), reverse=True)

  with open(filepath, 'w', encoding="utf-8") as f:
    json.dump(data, f, indent=4)
    
  print('Data refreshed!')
  return data

async def getMessages(ctx):
  print('Retrieving Message history...')
  messages = []
  async for message in ctx.channel.history(limit=None):
    messages.append(message)
  print('Messages retrieved!')
  return messages

async def getScores():
  with open(filepath, 'r') as f:
    members = json.load(f)

  userList = []
  for user in members:
    Name = user["Name"]
    Count = int(user["Mentions"])
    userList.append([Name, Count])

  print(userList)

  return userList

#Get all quotes of a specified member
async def getMentions(member, ctx):
  quotes = ""
  quote = ""
  channel = dc.utils.get(ctx.guild.channels, name=os.getenv('quoteChannel'))
  print(f'Searching for mentions in {channel}...')
  async for message in channel.history(limit=None):
    if member in message.mentions:
      quote = str(message.content)
      for mentioned in message.mentions:
        quote = quote.replace(f'<@!{mentioned.id}>', f'@{mentioned.name}').replace(f'<@{mentioned.id}>', f'@{mentioned.name}')

      quotes += quote + "\n\n"
  print('All mentions Found!')
  with open(txtdump, 'w', encoding='utf-8') as f:
    f.write(quotes)

#Secret
async def getLuddy(ctx):
  print("Fetching the Luddy quotes...")
  IDs = [834631585596309515, 793018805239808030, 728870835170967593, 720528612167778365]
  quotes = ""
  quote = ""
  channel = dc.utils.get(ctx.guild.channels, name=os.getenv('quoteChannel'))
  for ID in IDs:
    message = await channel.fetch_message(ID)
    quotes += message.content.replace("<@!336001822177099776>", "@LuddyLion").replace("<@336001822177099776>", "@LuddyLion") + "\n\n"

  quotes
  print('The Luddy Quotes have been Fetched!')
  with open(txtdump, 'w', encoding='utf-8') as f:
    f.write(quotes)


#Get a random message from the quotes channel
async def getRandom(ctx):
  print("Getting a random quote...")
  quote = ""
  messages = []
  channel = dc.utils.get(ctx.guild.channels, name=os.getenv('quoteChannel'))
  async for m in channel.history(limit=None):
    messages.append(m)
  message = rand.choice(messages)
  quote = str(message.content)

  for mentioned in message.mentions:
    quote = quote.replace(f'<@!{mentioned.id}>', f'@{mentioned.name}').replace(f'<@{mentioned.id}>', f'@{mentioned.name}')
  print('Got a Random Quote!')

  return quote


@bot.event
async def on_message(message):
  if message.author.bot:
    print('Message is from bot')

    await bot.process_commands(message)
    return

  if message.content.startswith("q."):
    print('Message is a Command (starts with q.)')

    await bot.process_commands(message)
    return

  else:
    print(message.channel)
    if str(message.channel) == os.getenv('quoteChannel') and len(message.mentions) > 0:
      messages = await getMessages(message)
      await count(message, messages)


  await bot.process_commands(message)
  return


#Send a message to Console when Bot is Ready
@bot.event
async def on_ready():
  print(f'Bot connected as {bot.user}')


#Funny Joke Command
@bot.command()
async def bingchilling(ctx):
  await ctx.send("早上好中国现在我有冰淇淋")


#Initiallizes Leaderboard Location
@bot.command()
async def init(ctx):
  print('Initializing Leaderboard...')
  await count(ctx)
  print('Leaderboard Initialized for Channel \"' + str(ctx.channel) + '\"!')


#retrieves scores and sends an embedded leaderboard
@bot.command()
async def leaderboard(ctx):

  list = await getScores()

  em = dc.Embed(title='Most Quoted Members:', color=0xffbf00)

  index = 1
  for user in list:
    em.add_field(name=f'{index}. {list[index-1][0]}',
                 value=f'{list[index-1][1]} Quotes',
                 inline=False)
    index += 1
  em.set_footer(text="Brought to you by: CarrotBRRR")
  await ctx.send(embed=em)

@bot.command()
async def random(ctx):
  rand = await getRandom(ctx)
  em = dc.Embed(title='Your Random Quote is:', color=0xffbf00)
  em.add_field(name=rand, value="")
  em.set_footer(text='Truly Words of Wisdom...')
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
      rand = await getRandom(ctx)
      await ctx.message.author.send(rand)

    else:
      await ctx.send('Invalid Number of Users...')
      return
    
  else:
    await getMentions(user[0], ctx)
    await ctx.message.author.send(f"Here is the quotes of {user[0]}: ", file=dc.File(txtdump))


bot.run(os.getenv('TOKEN'))
