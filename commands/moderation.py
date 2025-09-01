import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone
from Cogs.Methods.asynchronous.methods import logChannel
from Cogs.Methods.methods import permission_check, log
from DataBases.database import modlog, server_roles

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Give a warning to a user")
    @app_commands.describe(user="Enter a user", reason="Enter a reason", message="Optional Message")
    @app_commands.guild_only()
    @permission_check()
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str, message: str = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        if user.bot:
            await interaction.response.send_message(f"You can not warn {user.mention}, they are a bot!", ephemeral=True)
            return
        allowed_roles = server_roles(False, interaction)
        for role in user.roles:
            if str(role.id) in allowed_roles:
                await interaction.response.send_message(f"You may not warn {user.mention} as they have the role <@&{role.id}> and are a moderator!", ephemeral=True)
                return
        data = ( user.id, interaction.user.id, reason, message, "WARNING", datetime.now().astimezone(timezone.utc).strftime("[%d|%m|%y] : [%H:%M]"))
        await interaction.response.send_message(modlog(True, interaction, data), ephemeral=True)
        await logChannel(self.bot, interaction, data, user)

    @app_commands.command(name="ban", description="Ban a user")
    @app_commands.describe(user="Enter a user", reason="Enter a reason", message="Optional Message")
    @app_commands.guild_only()
    @permission_check()
    async def ban(self, interaction: discord.Interaction, user: discord.User, reason: str, message: str = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        if user.bot:
            await interaction.response.send_message(f"You can not warn {user.mention}, they are a bot!", ephemeral=True)
            return
        user = self.bot.get_user(user.id)
        allowed_roles = server_roles(False, interaction)
        for role in user.roles:
            if str(role.id) in allowed_roles:
                await interaction.response.send_message(f"You may not ban {user.mention} as they have the role <@&{role.id}> and are a moderator!", ephemeral=True)
                return
        data = ( user.id, interaction.user.id, reason, message, "BAN", datetime.now().astimezone(timezone.utc).strftime("[%d|%m|%y] : [%H:%M]"))
        await interaction.response.send_message(modlog(True, interaction, data), ephemeral=True)
        await user.ban(delete_message_seconds=0, reason=reason)
        await logChannel(self.bot, interaction, data, user)

    @app_commands.command(name="unban", description="Unban a user")
    @app_commands.describe(user="Enter a user", reason="Enter a reason")
    @app_commands.guild_only()
    @permission_check()
    async def unban(self, interaction: discord.Interaction, user: discord.User, reason: str = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        if user.bot:
            await interaction.response.send_message(f"{user.mention} is a bot, and are MOST likely not banned!", ephemeral=True)
            return
        user = self.bot.fetch_user(user.id)
        try:
            await interaction.guild.fetch_ban(user)
        except discord.NotFound:
            await interaction.response.send_message(f"{user.mention} is not banned!", ephemeral=True)
            return

        data = ( user.id, interaction.user.id, reason, None, "UNBAN", datetime.now().astimezone(timezone.utc).strftime("[%d|%m|%y] : [%H:%M]"))
        await user.unban(reason=reason)
        await logChannel(self.bot, interaction, data, user)
        await interaction.response.send_message(f"{user.mention} was successfully unbanned{f" with the reason: {reason}" if not reason == None else ""}!", ephemeral=True)

    @app_commands.command(name="modlogs", description="View the moderation log of a member (Timezone: UTC)")
    @app_commands.describe(user="Enter a user")
    @app_commands.guild_only()
    @permission_check()
    async def modlogs(self, interaction: discord.Interaction, user: discord.Member):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        if user.bot:
            await interaction.response.send_message(f"You can not view the warnings of {user.mention}, they are a bot!", ephemeral=True)
            return
        await interaction.response.send_message(embed=modlog(False, interaction, user=user), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))