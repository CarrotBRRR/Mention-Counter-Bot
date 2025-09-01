import discord as dc
from discord.ext import commands
import operator as op

from storage import get_leaderboard, set_leaderboard

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def count(self, ctx):
        guild_info = [g for g in self.bot.guilds if g.id == ctx.guild.id][0]
        counts = []
        for member in ctx.guild.members:
            if not member.bot:
                c, a = 0, 0
                for message in guild_info.messages:
                    if member in message.mentions and member != message.author:
                        c += 1
                    if member == message.author and len(message.mentions) >= 1:
                        if member not in message.mentions:
                            a += 1
                if c > 0 or a > 0:
                    counts.append({"Name": member.name, "Mentions": c, "Authored": a})

        counts.sort(key=op.itemgetter("Mentions"), reverse=True)
        set_leaderboard(ctx.guild.id, counts)
        return counts

    @commands.hybrid_command(name="rank", description="Get your rank in the leaderboard!")
    async def rank(self, ctx, user: dc.Member = None):
        member = user or ctx.author
        leaderboard = get_leaderboard(ctx.guild.id)
        em = dc.Embed(title=f"{member.name}'s Rank:", color=0xffbf00)

        rank_val, user_data = None, {"Mentions": 0, "Authored": 0}
        for i, entry in enumerate(leaderboard):
            if entry["Name"] == member.name:
                rank_val = i + 1
                user_data = entry
                break

        em.add_field(name="Rank", value=f"{rank_val}", inline=False)
        em.add_field(name="Mentions", value=f"{user_data['Mentions']}", inline=False)
        em.add_field(name="Authored", value=f"{user_data['Authored']}", inline=False)
        em.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=em)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
