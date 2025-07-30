import discord
from discord import app_commands
from discord.ext import commands
from DataBases.database import server_settings

class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverconfig", description="Change the configuration of the server for the bot.")
    @app_commands.describe(role="Add a Moderator/Admin role")
    @app_commands.guild_only()
    async def serverconfig(self, interaction: discord.Interaction, role: discord.Role):
        if interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(server_settings(True, interaction, role.id), ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission to run this command!")

async def setup(bot):
    await bot.add_cog(Server(bot))
