import discord
from discord import app_commands
from discord.ext import commands
from DataBases.database import server_roles, modlogchannel
from Cogs.Methods.methods import log
from Cogs.Classes.DiscordViews import Config

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

async def setup(bot):
    await bot.add_cog(Server(bot))
