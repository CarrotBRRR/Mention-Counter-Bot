import os, json, operator
import discord as dc
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()

# Setting JSON Filename
filepath = os.getenv('filepath')

# Setting Intents
intents = dc.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="q.", intents=intents)
guildID = os.getenv('guildID')


# Counts number of times mentioned in a channel,
# given the Context
# Warning: Highly inneficient
async def count(ctx):
  data = []
  guild = ctx.message.channel.guild

  print('Beginning Count...')

  for member in guild.members:
    if not member.bot:
      c = 0
      print('Counting for user ' + str(member) + '...')

      async for message in ctx.channel.history(limit=None):
        if member in message.mentions:
          c += 1
      if c > 0:
        obj = {
            "Name": str(member),
            "Mentions": int(c),
            "Channel": str(ctx.channel)
        }
        data.append(obj)

  print('Finished Counting for All Members!')
  data.sort(key=operator.itemgetter('Mentions'), reverse=True)

  with open(filepath, 'w', encoding="utf-8") as f:
    json.dump(data, f, indent=4)

  return data


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
    if str(message.channel) == os.getenv('quoteChannel'):
      ctx = await bot.get_context(message)
      await count(ctx)
      print('Data refreshed!')

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


#
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

bot.run(os.getenv('TOKEN'))
