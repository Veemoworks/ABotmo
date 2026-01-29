import discord, asyncio
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from Cogs.Methods.asynchronous.methods import logChannel, sendCase
from Cogs.Methods.methods import permission_check, log
from Cogs.Classes.DiscordViews import AutoBugReport
from DataBases.database import modlog, server_settings

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Give a warning to a user")
    @app_commands.describe(user="Enter a user", reason="Enter a reason", message="Optional Message")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @permission_check()
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str, message: str = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        if user.bot:
            await interaction.response.send_message(f"You can not warn {user.mention}, they are a bot!", ephemeral=True)
            return
        allowed_roles = server_settings(False, interaction.guild, "roles")
        for role in user.roles:
            if str(role.id) in allowed_roles:
                await interaction.response.send_message(f"You may not warn {user.mention} as they have the role <@&{role.id}> and are a moderator!", ephemeral=True)
                return
        data = [ user.id, interaction.user.id, reason, message, "WARNING", int(datetime.now().timestamp())]
        await interaction.response.send_message(modlog(True, interaction, data), ephemeral=True)
        server_settings(True, interaction.guild, "casenum")
        await logChannel(self.bot, interaction, data, user)
        await sendCase(interaction, data, user)

    @app_commands.command(name="mute", description="Timeout a user for a specific duration")
    @app_commands.describe(user="Enter a user", length="Enter a time (60s, 1m, 1h, 1d, 2w)", reason="Enter a reason")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @permission_check()
    async def mute(self, interaction: discord.Interaction, user: discord.Member, length: str, reason: str):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f'{interaction.guild.id} ({interaction.guild.name})' if interaction.guild else 'DMs'}!"))
        if user.bot:
            await interaction.response.send_message(f"You can not mute {user.mention}, they are a bot!", ephemeral=True)
            return

        allowed_roles = server_settings(False, interaction.guild, "roles")
        for role in user.roles:
            if str(role.id) in allowed_roles:
                await interaction.response.send_message(f"You may not mute {user.mention} as they have the role <@&{role.id}> and are a moderator!", ephemeral=True)
                return

        unit = length[-1]
        amount = int(length[:-1])

        if unit == "s":
            delta = timedelta(seconds=amount)
        elif unit == "m":
            delta = timedelta(minutes=amount)
        elif unit == "h":
            delta = timedelta(hours=amount)
        elif unit == "d":
            delta = timedelta(days=amount)
        elif unit == "w":
            delta = timedelta(weeks=amount)
        else:
            await interaction.response.send_message("Invalid time format! Use s/m/h/d/w.", ephemeral=True)
            return

        now = discord.utils.utcnow()
        t = now + timedelta(days=28)

        until = now + delta
        if until > t:
            until = t

        try:
            await user.timeout(until, reason=reason)
            data = [ user.id, interaction.user.id, reason, f"Muted for {length}", "MUTE", int(datetime.now().timestamp())]
            await interaction.response.send_message(modlog(True, interaction, data), ephemeral=True)
            server_settings(True, interaction.guild, "casenum")
            await logChannel(self.bot, interaction, data, user)
            await sendCase(interaction, data, user)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while running this command!\nError: {e}", view=AutoBugReport(interaction, e), ephemeral=True)

    @app_commands.command(name="unmute", description="Remove a timeout from a user")
    @app_commands.describe(user="Enter a user", reason="Enter a reason")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @permission_check()
    async def unmute(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f'{interaction.guild.id} ({interaction.guild.name})' if interaction.guild else 'DMs'}!"))
        if user.bot:
            await interaction.response.send_message(f"{user.mention} is a bot, they are most likely not muted!", ephemeral=True)
            return

        try:
            if user.is_timed_out():
                await user.timeout(discord.utils.utcnow(), reason=reason)
                data = [ user.id, interaction.user.id, reason, None, "UNMUTE", int(datetime.now().timestamp())]
                await interaction.response.send_message(f"Successfully unmuted {user.mention}!", ephemeral=True)
                server_settings(True, interaction.guild, "casenum")
                await logChannel(self.bot, interaction, data, user)
                await sendCase(interaction, data, user)
            else:
                await interaction.response.send_message(f"{user.mention} is not muted!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while running this command!\nError: {e}", view=AutoBugReport(interaction, e), ephemeral=True)

    @app_commands.command(name="ban", description="Ban a user")
    @app_commands.describe(user="Enter a user", reason="Enter a reason", message="Optional Message", delete_msgs="Delete messages from the user within a certain amount of days.")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @permission_check()
    async def ban(self, interaction: discord.Interaction, user: discord.User, reason: str, message: str = None, delete_msgs: int = 0):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        if user.bot:
            await interaction.response.send_message(f"You can not ban {user.mention}, they are a bot!", ephemeral=True)
            return
        t = interaction.guild.get_member(user.id)
        allowed_roles = server_settings(False, interaction.guild, "roles")
        data = [ user.id, interaction.user.id, reason, message, "BAN", int(datetime.now().timestamp())]
        try:
            if not t == None:
                for role in t.roles:
                    if str(role.id) in allowed_roles:
                        await interaction.response.send_message(f"You may not ban {user.mention} as they have the role <@&{role.id}> and are a moderator!", ephemeral=True)
                        return
                server_settings(True, interaction.guild, "casenum")
                await sendCase(interaction, data, user)
                await t.ban(delete_message_days=delete_msgs, reason=reason)
            else:
                user = await self.bot.fetch_user(user.id)
                server_settings(True, interaction.guild, "casenum")
                await sendCase(interaction, data, user)
                await interaction.guild.ban(user, reason=reason, delete_message_days=delete_msgs)

            await interaction.response.send_message(modlog(True, interaction, data), ephemeral=True)
            await logChannel(self.bot, interaction, data, user)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while running this command!\nError: {e}", view=AutoBugReport(interaction, e), ephemeral=True)

    @app_commands.command(name="softban", description="Ban and instantly unban someone to clear their messages.")
    @app_commands.describe(user="Enter a user", reason="Enter a reason")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @permission_check()
    async def softban(self, interaction: discord.Interaction, user: discord.User, reason: str = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        if user.bot:
            await interaction.response.send_message(f"You can not softban {user.mention}, they are a bot!", ephemeral=True)
            return
        t = interaction.guild.get_member(user.id)
        allowed_roles = server_settings(False, interaction.guild, "roles")
        data = [ user.id, interaction.user.id, reason, None, "SOFTBAN", int(datetime.now().timestamp())]
        try:
            if not t == None:
                for role in t.roles:
                    if str(role.id) in allowed_roles:
                        await interaction.response.send_message(f"You may not softban {user.mention} as they have the role <@&{role.id}> and are a moderator!", ephemeral=True)
                        return
                server_settings(True, interaction.guild, "casenum")
                await sendCase(interaction, data, user)
                await t.ban(delete_message_days=7, reason="Softban")
                await asyncio.sleep(1)
                await t.unban(reason="Unbanning from softban")
            else:
                server_settings(True, interaction.guild, "casenum")
                await sendCase(interaction, data, user)
                user = await self.bot.fetch_user(user.id)
                await interaction.guild.ban(user, delete_message_days=7, reason="Softban")
                await asyncio.sleep(1)
                await interaction.guild.unban(user, reason="Unbanning from softban")
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while running this command!\nError: {e}", view=AutoBugReport(interaction, e), ephemeral=True)

        await interaction.response.send_message(modlog(True, interaction, data), ephemeral=True)
        await logChannel(self.bot, interaction, data, user)

    @app_commands.command(name="kick", description="Kick a user")
    @app_commands.describe(user="Enter a user", reason="Enter a reason", message="Optional Message")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @permission_check()
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str, message: str = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        if user.bot:
            await interaction.response.send_message(f"You can not kick {user.mention}, they are a bot!", ephemeral=True)
            return
        allowed_roles = server_settings(False, interaction.guild, "roles")
        for role in user.roles:
            if str(role.id) in allowed_roles:
                await interaction.response.send_message(f"You may not kick {user.mention} as they have the role <@&{role.id}> and are a moderator!", ephemeral=True)
                return
        try:
            data = [ user.id, interaction.user.id, reason, message, "KICK", int(datetime.now().timestamp())]
            server_settings(True, interaction.guild, "casenum")
            await sendCase(interaction, data, user)
            await interaction.response.send_message(modlog(True, interaction, data), ephemeral=True)
            await user.kick(reason=reason)
            await logChannel(self.bot, interaction, data, user)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while running this command!\nError: {e}", view=AutoBugReport(interaction, e), ephemeral=True)

    @app_commands.command(name="unban", description="Unban a user")
    @app_commands.describe(user="Enter a user", reason="Enter a reason")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @permission_check()
    async def unban(self, interaction: discord.Interaction, user: discord.User, reason: str = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        if user.bot:
            await interaction.response.send_message(f"{user.mention} is a bot, and are MOST likely not banned!", ephemeral=True)
            return

        user = await self.bot.fetch_user(user.id)
        try:
            await interaction.guild.fetch_ban(user)
        except discord.NotFound:
            await interaction.response.send_message(f"{user.mention} is not banned!", ephemeral=True)
            return

        try:
            data = [ user.id, interaction.user.id, reason, None, "UNBAN", int(datetime.now().timestamp())]
            await interaction.guild.unban(user, reason=reason)
            server_settings(True, interaction.guild, "casenum")
            await logChannel(self.bot, interaction, data, user)
            await interaction.response.send_message(f"{user.mention} was successfully unbanned{f" with the reason: {reason}" if not reason == None else ""}!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while running this command!\nError: {e}", view=AutoBugReport(interaction, e), ephemeral=True)

    @app_commands.command(name="message", description="Message a user")
    @app_commands.describe(user="Enter a user", message=r"Enter the message you'd like to send (\ for a new line)")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @permission_check()
    async def msg(self, interaction: discord.Interaction, user: discord.Member, message: str):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.defer(ephemeral=True)
        if user.bot:
            await interaction.followup.send(f"{user.mention} is a bot, they don't need messages!")
            return
        elif user.id == interaction.user.id:
            await interaction.followup.send(f"You may not message yourself!")
            return

        message = message.replace("\\", "\n")
        data = [ user.id, interaction.user.id, message, None, "MESSAGE", int(datetime.now().timestamp())]
        case = server_settings(True, interaction.guild, "casenum")
        embed = discord.Embed(title=f"You have recieved a **MESSAGE** from __**{interaction.guild.name}**__!", description=f"-# CASE {case}",color=discord.Color.brand_green())
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_author(name=f"{interaction.guild.name} | {interaction.guild.id}", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.add_field(name="Message:", value=message, inline=False)
        embed.timestamp = datetime.now()

        try:
            await user.send(embed=embed)
            await logChannel(self.bot, interaction, data, user)
            await interaction.followup.send(f'{user.mention} was successfully messaged:\n"{message}"!')
        except Exception as e:
            await interaction.followup.send(f"An error occurred while running this command!\nError: {e}", view=AutoBugReport(interaction, e))

    @app_commands.command(name="modlogs", description="View the moderation logs of a member")
    @app_commands.describe(user="Enter a user", page="Page number (each page has a limit of 25 modlogs)")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @permission_check()
    async def modlogs(self, interaction: discord.Interaction, user: discord.User, page: int = 1):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.defer(ephemeral=True)
        if user.bot:
            await interaction.response.send_message(f"You can not view the warnings of {user.mention}, they are a bot!", ephemeral=True)
            return
        if page < 1:
            await interaction.followup.send("Please enter a page number thats bigger than 0!")
            return
        await interaction.followup.send(embed=modlog(False, interaction, [page, False], user))

    @app_commands.command(name="checkmod", description="View the moderation logs a moderator has done")
    @app_commands.describe(user="Enter a user", page="Page number (each page has a limit of 25 modlogs)")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @permission_check()
    async def checkmod(self, interaction: discord.Interaction, user: discord.User, page: int = 1):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.defer(ephemeral=True)
        if user.bot:
            await interaction.followup.send(f"You can not view the warnings of {user.mention}, they are a bot!", ephemeral=True)
            return
        if page < 1:
            await interaction.followup.send("Please enter a page number thats bigger than 0!")
            return
        modlogs = modlog(False, interaction, [page, True], user)
        await interaction.followup.send(embeds=[modlogs])

    @app_commands.command(name="remlog", description="Remove a moderation log")
    @app_commands.describe(user="User to remove from", index="Index number of the moderation log (* for all)", reason="Reason to remove")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @permission_check()
    async def remlog(self, interaction: discord.Interaction, user: discord.User, index: str, reason: str = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        if user.bot:
            await interaction.response.send_message(f"You can not remove a mod log from {user.mention}, they are a bot!", ephemeral=True)
            return
        if not index.isnumeric():
            if not index == "*":
                await interaction.response.send_message(f"Please input a number or \"*\" and not {index}", ephemeral=True)
                return
        else:
            index = int(index)

        thing = modlog(True, interaction, index, user, True)

        await interaction.response.send_message(thing[0], ephemeral=True)
        if thing[1]:
            server_settings(True, interaction.guild, "casenum")
            await logChannel(self.bot, interaction, [ user.id, interaction.user.id, index, reason, "MODLOG REMOVAL", int(datetime.now().timestamp())], user)

    @app_commands.command(name="mylogs", description="See your log count for this server!")
    @app_commands.guild_only()
    @app_commands.allowed_contexts(True, False, False)
    async def mylogs(self, interaction: discord.Interaction):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.defer(ephemeral=True)
        amt = modlog(False, interaction, user=interaction.user, rem=True)
        embed = discord.Embed(description=f"You have {amt} modlogs!",color=discord.Color.brand_green())
        embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.timestamp = datetime.now()

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))