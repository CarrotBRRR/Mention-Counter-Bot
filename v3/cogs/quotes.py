import discord as dc
from discord.ext import commands
import random as rand

class Quotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="random", description="Get a random quote")
    async def random_quote(self, ctx):
        guild_info = [g for g in self.bot.guilds if g.id == ctx.guild.id][0]
        if not guild_info.hasMessages():
            await ctx.send("No quotes cached yet.")
            return

        message = rand.choice(guild_info.messages)
        em = dc.Embed(
            title="Your Random Message:",
            color=0xffbf00,
            url=f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}",
        )
        em.add_field(name="", value=message.content)
        await ctx.send(embed=em)

async def setup(bot):
    await bot.add_cog(Quotes(bot))
