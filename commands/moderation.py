import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone
from Cogs.Methods.methods import permission_check, log
from DataBases.database import modlog

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Give a warning to a user")
    @app_commands.describe(user="Enter a user", reason="Enter a reason", message="Optional Message")
    @app_commands.guild_only()
    @permission_check()
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str, message: str = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id}!"))
        if user.bot:
            await interaction.response.send_message(f"You can not warn {user.mention}, they are a bot!", ephemeral=True)
            return
        data = ( user.id, interaction.user.id, reason, message, "WARNING", datetime.now().astimezone(timezone.utc).strftime("[%d|%m|%y] : [%H:%M]"))
        await interaction.response.send_message(modlog(True, interaction, data), ephemeral=True)

    @app_commands.command(name="modlogs", description="View the moderation log of a member (Timezone: UTC)")
    @app_commands.describe(user="Enter a user")
    @app_commands.guild_only()
    @permission_check()
    async def modlogs(self, interaction: discord.Interaction, user: discord.Member):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id}!"))
        if user.bot:
            await interaction.response.send_message(f"You can not view the warnings of {user.mention}, they are a bot!", ephemeral=True)
            return
        await interaction.response.send_message(embed=modlog(False, interaction, user=user), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))