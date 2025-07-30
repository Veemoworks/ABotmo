import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Give a warning to a user")
    @app_commands.describe(user="Enter a user", reason="Enter a reason", message="Optional Message")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str, message: str = None):
        print(f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name}! {datetime.now().strftime("[%d|%m|%y] : [%H:%M]")}")
        if user.bot:
            await interaction.response.send_message(f"You can not warn {user.mention}, they are a bot!", ephemeral=True)
            return

        await interaction.response.send_message(f"you're a noob {user.mention}, {reason} {message if not message is None else message}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))