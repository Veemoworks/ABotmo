import discord, asyncio
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from Cogs.Methods.asynchronous.methods import logChannel, sendCase
from Cogs.Methods.methods import canUse, log
from Cogs.Classes.DiscordViews import AutoBugReport
from Cogs.Classes.DiscordModals import AppealLog
from Cogs.database import modlog, server_settings

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Give a warning to a user")
    @app_commands.describe(user="Enter a user", reason="Enter a reason", message="Optional Message")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @canUse()
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str, message: str = None, appealable: bool = True):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.defer(ephemeral=True)
        if user.bot:
            await interaction.followup.send(f"You can not warn {user.mention}, they are a bot!")
            return
        allowed_roles = server_settings(False, interaction.guild, "roles")
        for role in user.roles:
            if str(role.id) in allowed_roles:
                await interaction.followup.send(f"You may not warn {user.mention} as they have the role <@&{role.id}> and are a moderator!")
                return
        data = [ user.id, interaction.user.id, reason, message, "WARNING", int(datetime.now().timestamp()), appealable]
        msg = modlog(True, interaction, data)
        data.append(msg[1])
        server_settings(True, interaction.guild, "casenum")
        await logChannel(self.bot, interaction, data, user)
        success, msg2 = await sendCase(interaction, data, user, appealable)
        await interaction.followup.send(msg[0] + "" if success else f"\n\nThe user has still recieved the {data[4]}, but not a DM\n-# Error: {msg2}")

    @app_commands.command(name="mute", description="Timeout a user for a specific duration")
    @app_commands.describe(user="Enter a user", length="Enter a time (60s, 1m, 1h, 1d, 2w)", reason="Enter a reason")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @canUse()
    async def mute(self, interaction: discord.Interaction, user: discord.Member, length: str, reason: str = None, appealable: bool = True):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f'{interaction.guild.id} ({interaction.guild.name})' if interaction.guild else 'DMs'}!"))
        await interaction.response.defer(ephemeral=True)
        if user.bot:
            await interaction.followup.send(f"You can not mute {user.mention}, they are a bot!")
            return

        allowed_roles = server_settings(False, interaction.guild, "roles")
        for role in user.roles:
            if str(role.id) in allowed_roles:
                await interaction.followup.send(f"You may not mute {user.mention} as they have the role <@&{role.id}> and are a moderator!")
                return

        unit = length[-1]
        amount = int(length[:-1])

        match unit:
            case "s":
                delta = timedelta(seconds=amount)
            case "m":
                delta = timedelta(minutes=amount)
            case "h":
                delta = timedelta(hours=amount)
            case "d":
                delta = timedelta(days=amount)
            case "w":
                delta = timedelta(weeks=amount)
            case _:
                await interaction.followup.send("Invalid time format! Use s/m/h/d/w.")
                return

        now = discord.utils.utcnow()
        t = now + timedelta(days=28)

        until = now + delta
        if until > t:
            until = t

        try:
            await user.timeout(until, reason=reason)
            data = [ user.id, interaction.user.id, reason, f"Muted for {length}", "MUTE", int(datetime.now().timestamp()), appealable]
            msg = modlog(True, interaction, data)
            data.append(msg[1])
            server_settings(True, interaction.guild, "casenum")
            await logChannel(self.bot, interaction, data, user)
            success, msg2 = await sendCase(interaction, data, user, appealable)
            await interaction.followup.send(msg[0] + "" if success else f"\n\nThe user has still recieved the {data[4]}, but not a DM\n-# Error: {msg2}")
        except Exception as e:
            await interaction.followup.send(f"An error occurred while running this command!\nError: {e}", view=AutoBugReport(interaction, e))

    @app_commands.command(name="unmute", description="Remove a timeout from a user")
    @app_commands.describe(user="Enter a user", reason="Enter a reason")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @canUse()
    async def unmute(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f'{interaction.guild.id} ({interaction.guild.name})' if interaction.guild else 'DMs'}!"))
        await interaction.response.defer(ephemeral=True)
        if user.bot:
            await interaction.followup.send(f"{user.mention} is a bot, they are most likely not muted!")
            return

        try:
            if user.is_timed_out():
                await user.timeout(discord.utils.utcnow(), reason=reason)
                data = [ user.id, interaction.user.id, reason, None, "UNMUTE", int(datetime.now().timestamp())]
                msg = modlog(True, interaction, data)
                data.append(msg[1])
                server_settings(True, interaction.guild, "casenum")
                await logChannel(self.bot, interaction, data, user)
                success, msg = await sendCase(interaction, data, user, False)
                await interaction.followup.send(f"Successfully unmuted {user.mention}!"+ "" if success else f"\n\nThe user has still recieved the {data[4]}, but not a DM\n-# Error: {msg}")
            else:
                await interaction.followup.send(f"{user.mention} is not muted!")
        except Exception as e:
            await interaction.followup.send(f"An error occurred while running this command!\nError: {e}", view=AutoBugReport(interaction, e))

    @app_commands.command(name="ban", description="Ban a user")
    @app_commands.describe(user="Enter a user", reason="Enter a reason", message="Optional Message", delete_msgs="Delete messages from the user within a certain amount of days.")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @canUse()
    async def ban(self, interaction: discord.Interaction, user: discord.User, reason: str = None, message: str = None, delete_msgs: int = 0, appealable: bool = True):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.defer(ephemeral=True)
        if user.bot:
            await interaction.followup.send(f"You can not ban {user.mention}, they are a bot!")
            return
        t = interaction.guild.get_member(user.id)
        allowed_roles = server_settings(False, interaction.guild, "roles")
        data = [ user.id, interaction.user.id, reason, message, "BAN", int(datetime.now().timestamp()), appealable]
        success, msg2 = True, ""
        try:
            if not t == None:
                for role in t.roles:
                    if str(role.id) in allowed_roles:
                        await interaction.followup.send(f"You may not ban {user.mention} as they have the role <@&{role.id}> and are a moderator!")
                        return
                msg = modlog(True, interaction, data)
                server_settings(True, interaction.guild, "casenum")
                success, msg2 = await sendCase(interaction, data, user, appealable)
                await t.ban(delete_message_days=delete_msgs, reason=reason)
            else:
                msg = modlog(True, interaction, data)
                user = self.bot.get_user(user.id)
                server_settings(True, interaction.guild, "casenum")
                await interaction.guild.ban(user, reason=reason, delete_message_days=delete_msgs)
            data.append(msg[1])
            await logChannel(self.bot, interaction, data, user)
            await interaction.followup.send(msg[0] + "" if success else f"\n\nThe user has still recieved the {data[4]}, but not a DM\n-# Error: {msg2}")
        except Exception as e:
            await interaction.followup.send(f"An error occurred while running this command!\nError: {e}", view=AutoBugReport(interaction, e))

    @app_commands.command(name="softban", description="Ban and instantly unban someone to clear their messages.")
    @app_commands.describe(user="Enter a user", reason="Enter a reason")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @canUse()
    async def softban(self, interaction: discord.Interaction, user: discord.User, reason: str = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.defer(ephemeral=True)
        if user.bot:
            await interaction.followup.send(f"You can not softban {user.mention}, they are a bot!")
            return
        t = interaction.guild.get_member(user.id)
        allowed_roles = server_settings(False, interaction.guild, "roles")
        data = [ user.id, interaction.user.id, reason, None, "SOFTBAN", int(datetime.now().timestamp())]
        msg, msg2 = "", ""
        success = True
        try:
            if not t == None:
                for role in t.roles:
                    if str(role.id) in allowed_roles:
                        await interaction.followup.send(f"You may not softban {user.mention} as they have the role <@&{role.id}> and are a moderator!")
                        return
                msg = modlog(True, interaction, data)
                server_settings(True, interaction.guild, "casenum")
                success, msg2 = await sendCase(interaction, data, user, False)
                await t.ban(delete_message_days=7, reason="Softban")
                await asyncio.sleep(1)
                await t.unban(reason="Unbanning from softban")
            else:
                msg = modlog(True, interaction, data)
                server_settings(True, interaction.guild, "casenum")
                user = self.bot.get_user(user.id)
                await interaction.guild.ban(user, delete_message_days=7, reason="Softban")
                await asyncio.sleep(1)
                await interaction.guild.unban(user, reason="Unbanning from softban")
        except Exception as e:
            await interaction.followup.send(f"An error occurred while running this command!\nError: {e}", view=AutoBugReport(interaction, e))
        data.append(msg[1])
        await logChannel(self.bot, interaction, data, user)
        await interaction.followup.send(msg[0] + "" if success else f"\n\nThe user has still recieved the {data[4]}, but not a DM\n-# Error: {msg2}")

    @app_commands.command(name="kick", description="Kick a user")
    @app_commands.describe(user="Enter a user", reason="Enter a reason", message="Optional Message")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @canUse()
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str, message: str = None, appealable: bool = True):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.defer(ephemeral=True)
        if user.bot:
            await user.kick(reason=reason)
            await interaction.followup.send(f"Successfully kicked bot {user.mention} ({user.id})!")
            return
        allowed_roles = server_settings(False, interaction.guild, "roles")
        for role in user.roles:
            if str(role.id) in allowed_roles:
                await interaction.followup.send(f"You may not kick {user.mention} as they have the role <@&{role.id}> and are a moderator!")
                return
        try:
            data = [ user.id, interaction.user.id, reason, message, "KICK", int(datetime.now().timestamp()), appealable]
            msg = modlog(True, interaction, data)
            data.append(msg[1])
            server_settings(True, interaction.guild, "casenum")
            success, msg2 = await sendCase(interaction, data, user, appealable)
            await user.kick(reason=reason)
            await logChannel(self.bot, interaction, data, user)
            await interaction.followup.send(msg[0] + "" if success else f"\n\nThe user has still recieved the {data[4]}, but not a DM\n-# Error: {msg2}")
        except Exception as e:
            await interaction.followup.send(f"An error occurred while running this command!\nError: {e}", view=AutoBugReport(interaction, e))

    @app_commands.command(name="unban", description="Unban a user")
    @app_commands.describe(user="Enter a user", reason="Enter a reason")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @canUse()
    async def unban(self, interaction: discord.Interaction, user: discord.User, reason: str = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.defer(ephemeral=True)
        if user.bot:
            await interaction.followup.send(f"{user.mention} is a bot, and are MOST likely not banned!")
            return

        try:
            await interaction.guild.fetch_ban(user)
        except discord.NotFound:
            await interaction.followup.send(f"{user.mention} is not banned!")
            return

        try:
            data = [ user.id, interaction.user.id, reason, None, "UNBAN", int(datetime.now().timestamp())]
            msg = modlog(True, interaction, data)
            data.append(msg[1])
            await interaction.guild.unban(user, reason=reason)
            server_settings(True, interaction.guild, "casenum")
            await logChannel(self.bot, interaction, data, user)
            await interaction.followup.send(f"{user.mention} was successfully unbanned{f" with the reason: {reason}" if not reason == None else ""}!")
        except Exception as e:
            await interaction.followup.send(f"An error occurred while running this command!\nError: {e}", view=AutoBugReport(interaction, e))

    @app_commands.command(name="message", description="Message a user")
    @app_commands.describe(user="Enter a user", message=r"Enter the message you'd like to send (\ for a new line)")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @canUse()
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
        case = server_settings(True, interaction.guild, "casenum")
        data = [ user.id, interaction.user.id, "Message: " + message, None, "MESSAGE", int(datetime.now().timestamp()), case, None]
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
    @app_commands.describe(user="Enter a user", logid="Log ID of a Moderation Log", page="Page number (each page has a limit of 25 modlogs)",)
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @canUse()
    async def modlogs(self, interaction: discord.Interaction, user: discord.User = None, logid: str = None, page: int = 1):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.defer(ephemeral=True)
        if user and user.bot:
            await interaction.followup.send(f"You can not view the modlogs of {user.mention}, they are a bot!")
            return
        if page < 1: page = 1
        if not user and not logid:
            await interaction.followup.send("Please enter either a user to see their full logs or a Log ID to see details of that log.")
            return
        await interaction.followup.send(embed=modlog(False, interaction, [page, logid, False], user))

    @app_commands.command(name="checkmod", description="View the moderation logs a moderator has done")
    @app_commands.describe(user="Enter a user", page="Page number (each page has a limit of 25 modlogs)")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @canUse()
    async def checkmod(self, interaction: discord.Interaction, user: discord.User, page: int = 1):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.defer(ephemeral=True)
        if user.bot:
            await interaction.followup.send(f"You can not view the modlogs of {user.mention}, they are a bot!")
            return
        if page < 1:
            await interaction.followup.send("Please enter a page number thats bigger than 0!")
            return
        modlogs = modlog(False, interaction, [page, None, True], user)
        await interaction.followup.send(embeds=[modlogs])

    @app_commands.command(name="remlog", description="Remove a moderation log")
    @app_commands.describe(logid="Log ID of the Moderation Log (* for all)", user="User to remove from (Required if deleting all logs)", reason="Reason to remove")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @canUse()
    async def remlog(self, interaction: discord.Interaction, logid: str, user: discord.User = None, reason: str = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.defer(ephemeral=True)
        if user and user.bot:
            await interaction.followup.send(f"You can not remove a mod log from {user.mention}, they are a bot!")
            return

        thing = modlog(True, interaction, logid, user, True)

        if thing[1]:
            await logChannel(self.bot, interaction, [thing[2], interaction.user.id, "Removed all Logs" if logid == "*" else f"Removed '{logid}'", reason, "MODLOG REMOVAL", int(datetime.now().timestamp()), thing[3], logid], interaction.guild.get_member(thing[2]))
        await interaction.followup.send(thing[0])

    @app_commands.command(name="mylogs", description="See your log count for this server!")
    @app_commands.guild_only()
    @app_commands.allowed_contexts(True, False, False)
    async def mylogs(self, interaction: discord.Interaction):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(description=f"You have {modlog(False, interaction, user=interaction.user, rem=True)} modlogs!",color=discord.Color.brand_green())
        embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        embed.timestamp = datetime.now()

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="appeal", description="Appeal a moderation log!")
    @app_commands.describe(guild="Enter a Guild ID if you're using this in DMs or if its in another server!")
    @app_commands.allowed_contexts(True, True, True)
    async def appeal(self, interaction: discord.Interaction, guild: str = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        if guild and guild.isnumeric():
            guild = self.bot.get_guild(guild)
        else:
            guild = interaction.guild

        if guild:
            if server_settings(False, guild, "appeal"):
                await interaction.response.send_modal(AppealLog(guild))
            else:
                await interaction.response.send_message(
                    "This server does not have appeals set up! Please contact the Server Owner / Admin to set it up!",
                    ephemeral=True)
        else:
            await interaction.response.send_message("No Guild found! Make sure to input a Guild ID into the \"guild\" parameter or use this in the Guild you want to appeal in", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))