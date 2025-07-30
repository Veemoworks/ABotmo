import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from DataBases.database import warnings

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Give a warning to a user")
    @app_commands.describe(user="Enter a user", reason="Enter a reason", message="Optional Message")
    @app_commands.guild_only()
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str, message: str = None):
        print(f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name}! {datetime.now().strftime("[%d|%m|%y] : [%H:%M]")}")
        if user.bot:
            await interaction.response.send_message(f"You can not warn {user.mention}, they are a bot!", ephemeral=True)
            return
        data = ( user.id, interaction.user.id, reason, message, datetime.now().strftime("[%d|%m|%y] : [%H:%M]"))
        await interaction.response.send_message(warnings(True, interaction, data), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))