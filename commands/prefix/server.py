import discord
from discord.ext import commands
from Cogs.Methods.methods import log
from Cogs.Methods.asynchronous.methods import get_prefix
from DataBases.database import xp

class ServerPREFIX(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.command(name="rank", description="Check your rank in this server!.")
    async def purge_prefix(self, ctx, user: discord.Member = None):
        prefix = await get_prefix(self.bot, ctx.message)
        print(log(False,f"{ctx.author} ({ctx.author.id}) used {prefix}{ctx.command.qualified_name} in {ctx.guild.id} ({ctx.guild.name})!"))
        has_perms = commands.bot_has_guild_permissions(embed_links=True)

        if user == None:
            user = ctx.author
        data, xpinfo = xp(False, ctx.guild, user=user)

        if data:
            currxp, level, nxt_lvl = xpinfo
            nxt_lvl -= currxp
            if has_perms:
                embed = discord.Embed(description=f"**Level**: {level}\n**XP**: {currxp}\n**{nxt_lvl} XP** needed.",
                                      color=discord.Color.brand_green())
                embed.set_author(name=f"@{user.name}'s XP for {ctx.guild.name}.",
                                 icon_url=user.display_avatar.url)
                await ctx.send(embed=embed)
            else:
                await ctx.send(
                    f"**__{user.name}__**\n**Level**: {level}\n**XP**: {currxp}\n**{nxt_lvl} XP** needed.")
        else:
            if has_perms:
                embed = discord.Embed(color=discord.Color.brand_green())
                embed.set_author(
                    name=f"@{user.name} has no XP {f"{f"for {ctx.guild.name}" if not ctx.guild.name == "" else "as an external app"}"}",
                    icon_url=user.display_avatar.url)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"**__{user.name}__** has no XP for {ctx.guild.name}.")

    # errors for commands

async def setup(bot):
    await bot.add_cog(ServerPREFIX(bot))