import discord as dc
from discord.ext import commands
from storage import get_config, set_config

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="setqchannel",
        description="(Admin Only) Set the quotes channel"
    )
    @commands.has_permissions(administrator=True)
    async def setQChannel(self, ctx, qchannel: dc.TextChannel):
        config = get_config(ctx.guild.id)
        config["Q Channel"] = qchannel.id
        set_config(ctx.guild.id, config)
        await ctx.send(f"{qchannel.mention} has been set as the quotes channel!")

async def setup(bot):
    await bot.add_cog(Admin(bot))
