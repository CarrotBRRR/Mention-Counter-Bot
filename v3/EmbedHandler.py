"""
This file contains the functions that create the embeds for the bot's messages.
"""

from discord import embeds
import discord

async def leaderboard_embed(channel, scores):
    embed = embeds.Embed(title='Most Quoted Members:', color=0xffbf00)
    embed.set_footer(text='Top 10 Most Quoted Members')

async def embed_random_quote(channel, quote, color=0xffbf00):
    em = embeds.Embed(title='Your Random Message:', color=0xffbf00, 
                url=f'https://discord.com/channels/{quote.guild.id}/{quote.channel.id}/{quote.id}')
    
    em.add_field(name="", value=quote.content)

    em.set_footer(text='Truly Words of Wisdom...')

    att_ems = []
    att_ems.append(em)

    # if len(message.attachments) != 0:
    for attachment in quote.attachments:
        att = embeds.Embed()
        att.set_image(url = attachment.url)
        att_ems.append(att)

    return att_ems
