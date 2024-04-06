import os, json, sys
import operator as op
import random as rand
import discord as dc
import typing

from discord.ext import commands as comms
from discord.utils import get
from dotenv import load_dotenv

from Guild import Guild
from GlobalLogger import GlobalLogger
from EmbedHandler import *

intents = dc.Intents.default()
intents.message_content = True
intents.members = True

bot = comms.Bot(command_prefix='q.', intents=intents)

load_dotenv()

global l
l = GlobalLogger()

global guilds
guilds: dict[str, Guild] = {}

@bot.event
async def on_ready():
    l.log(f'Logged in as {bot.user.name}')
    l.log(f'[INFO] Setting up Guilds...')

    # Empty the guilds dictionary
    guilds: dict[str, Guild] = {}

    for guild in bot.guilds:
        # Create a directory for the guild if it doesn't exist
        if not os.path.exists(guild_folder):
            os.mkdir(guild_folder)
            os.makedirs(guild_folder, exist_ok=True)
            l.log(f'\t[INFO] Created Directory for {guild.name}')

        # Create a Guild object for the guild
        guilds[str(guild.id)] = Guild(guild)
        guild_folder = f'./data/{guild.id}'
        l.log(f'\t[INFO] Created Guild Object for {guild.name}')
    
    l.log(f'[INFO] Guilds Setup Complete!')

# ------------------------- Message Events ------------------------- #

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    text = str(message.content).replace("\n","\n\t")
    l.log(f'+ [{message.guild}] ({message.channel}) {message.author}: {text}')

    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or after.author.bot:
        return

    before_text = str(before.content).replace("\n","\n\t")
    after_text = str(after.content).replace("\n","\n\t")

    l.log(f'* [{before.guild}] ({before.channel}) {before.author} edited message:\n\t   {before_text.content}\n\t-> {after_text.content}')

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    text = str(message.content).replace("\n","\n\t")
    l.log(f'- [{message.guild}] ({message.channel}) {message.author}: {text}')

# ------------------------- Guild Events ------------------------- #

@bot.event
async def on_guild_join(guild):
    l.log(f'[INFO] Joined Guild: {guild.name}!\n\tSetting up Guild...')

    guild_folder = f'./data/{guild.id}'
    if not os.path.exists(guild_folder):
        os.mkdir(guild_folder)
        os.makedirs(guild_folder, exist_ok=True)
        l.log(f'\t[INFO] Created Directory for {guild.name}')
    
    guilds[str(guild.id)] = Guild(guild)

    l.log(f'[INFO] Guild Setup for {guild.name} Complete!')

@bot.event
async def on_guild_remove(guild):
    l.log(f'[INFO] Left Guild: {guild.name}!\n\tRemoving Guild from List...')
    
    guilds.pop(str(guild.id))

    l.log(f'[INFO] Guild {guild.name} Removed!')

@bot.event
async def on_guild_channel_create(channel):
    guilds[str(channel.guild.id)].channels.add_channel(channel)

    l.log(f'[INFO] Added Channel {channel.name} to Guild {channel.guild.name}')

@bot.event
async def on_guild_channel_delete(channel):
    guilds[str(channel.guild.id)].channels.remove_channel(channel)

    l.log(f'[INFO] Removed Channel {channel.name} from Guild {channel.guild.name}')

# ------------------------- Command Events ------------------------- #
@bot.hybrid_command(
    name="random",
    brief="Get a random message from a channel!",
    description="Defaults to the quotes channel if none is provided.",
    aliases=["r"]
)
async def random(ctx, channel: typing.Optional[dc.TextChannel] = None):
    if channel is None:
        channel = guilds[str(ctx.guild.id)].config.qchannel
        if channel == 0:
            await ctx.send("Please provide a #channel\nor /setqchannel to set the quotes channel", ephemeral=True, delete_after=5)
            return

    l.log(f'[INFO] ({channel.guild.name}) Getting a random message from {channel.name}...')

    res = await ctx.send(f'Getting a random message from {channel.name}...')

    # Get a random message from the channel
    random_id = guilds[str(ctx.guild.id)].get_random_message(channel)
    message = await channel.fetch_message(random_id)

    # Create the embeds for the message
    ems = await embed_random_quote(channel, message)
    if ems is None or ems == []:
        await res.edit(content=f'No messages found in {channel}', delete_after=5)
        return
    
    # Send first 10 embeds as an edit response (Discord only allows 10 embeds per message)
    if len(ems) > 10:
        await res.edit(content=None, embeds=ems[:10])
    i = len(ems)

    # Send the embeds in groups of 10
    while i > 0:
        i -= 10
        ems = ems[10:]
        if i > 10:
            await ctx.send(content=None, embeds=ems[:10])
        elif i > 0 and i <= 10:
            await ctx.send(content=None, embeds=ems)
    else:
        await res.edit(content=None, embeds=ems)

bot.remove_command('help')
bot.run(os.getenv('TESTTOKEN'))