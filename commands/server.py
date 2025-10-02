import discord
from discord import app_commands
from discord.ext import commands
from Cogs.Methods.methods import log
from Cogs.Classes.DiscordViews import Config
from DataBases.database import xp

class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverconfig", description="Change the configuration of the server for the bot.")
    @app_commands.guild_only()
    async def serverconfig(self, interaction: discord.Interaction):
        print(log(False,
                  f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id} ({interaction.guild.name})!"))
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to run this command!", ephemeral=True)
            return

        embed = discord.Embed(
            title="Server Configuration",
            description=f"Welcome to the Server Configuration Panel, {interaction.user.mention}!\n"
                        "Only Administrators can access this menu.\n\n"
                        "Choose what you’d like to configure below:",
            color=discord.Color.brand_green()
        )
        view = Config(interaction)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="rank", description="Check your rank in this server!")
    @app_commands.guild_only()
    async def rank(self, interaction: discord.Interaction, user: discord.Member = None):
        print(log(False,f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id} ({interaction.guild.name})!"))
        has_perms = app_commands.checks.bot_has_permissions(embed_links=True)

        if user == None:
            user = interaction.user
        data, xpinfo = xp(False, interaction.guild, user=user)

        if data:
            currxp, level, nxt_lvl = xpinfo
            nxt_lvl -= currxp
            if has_perms:
                embed = discord.Embed(description=f"**Level**: {level}\n**XP**: {currxp}\n**{nxt_lvl} XP** needed.", color=discord.Color.brand_green())
                embed.set_author(name=f"@{user.name}'s XP for {interaction.guild.name}.", icon_url=user.display_avatar.url)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"**__{user.name}__**\n**Level**: {level}\n**XP**: {currxp}\n**{nxt_lvl} XP** needed.")
        else:
            if has_perms:
                embed = discord.Embed(color=discord.Color.brand_green())
                embed.set_author(name=f"@{user.name} has no XP {f"{f"for {interaction.guild.name}" if not interaction.guild.name == "" else "as an external app"}"}", icon_url=user.display_avatar.url)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"**__{user.name}__** has no XP for {interaction.guild.name}.")

async def setup(bot):
    await bot.add_cog(Server(bot))
