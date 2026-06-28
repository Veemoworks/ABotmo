import discord, platform, time, os, re
from datetime import datetime
from discord.ext import commands
from Cogs.Methods.methods import crash, log, levelCard, permCheck, toDiscordTimestamp
from resources.dictionaries import custom_urls
from resources.links import warm
from resources.variables import pid, version, noMentions, noRoleMentions
from Cogs.Methods.asynchronous.botStatus import status, kuma, ramthing
from Cogs.Methods.asynchronous.methods import event, get_prefix
from Cogs.database import xp, user_settings, xp_settings, xp_roles, server_settings

class Events(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.bot = client

    done = False
    errorembed = discord.Embed(title="Bot Error!",
                               description="An error occurred while running this command!\n### Possible reasons:\n- A freak error. Try again.\n- This command is in beta/outdated.\n- I'm slow at responding, check </stats:1441449914352533664>.\n- If this error lasts for days, shoot us a </bugreport:1396647997290319905>!",
                               color=discord.Color.dark_green())
    errorembed.set_thumbnail(url=warm)

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            try:
                if not self.done:
                    # Load cogs
                    cogs = ["fun", "utils", "moderation", "server", "prefix.utils", "prefix.server"]
                    for cog in cogs:
                        await self.bot.load_extension(f"commands.{cog}")
                    # Sync self.bot tree.
                    synced = await self.bot.tree.sync()
                    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                    thing = (f"[{now}] [INFO    ] ABotmo v{version}\n"
                             f"[{now}] [INFO    ] Logged in as {self.bot.user}\n"
                             f"[{now}] [INFO    ] discord.py V{discord.__version__}\n"
                             f"[{now}] [INFO    ] Python {platform.python_version()}\n"
                             f"[{now}] [INFO    ] Running on: {platform.system()} {platform.release()} ({os.name})\n"
                             f"[{now}] [INFO    ] Application ID: {pid}\n"
                             f"[{now}] [INFO    ] Synced {len(synced)} commands\n"
                             f"[{now}] [INFO    ] Registering new commands from: {", ".join(cogs)}.\n"
                             )
                    print(thing, end="")
                    with open("output.txt", "a") as r:
                        r.write(thing.removeprefix("\033[92m"))
                    cmds = await self.bot.tree.fetch_commands()
                    for command in cmds:
                        print(log(False, f"Command {command.name} (</{command.name}:{command.id}>) Registered!"))
                    # Bot Loops
                    ramthing.start()
                    status.start(self.bot)
                    kuma.start(self.bot)
                    t = self.bot.get_channel(1403041372751265912)
                    await t.edit(name="[ 🟢 ] | Bot Status: Online")
                    print(log(False, f"READY TO KILL ALL FELLAS..."))
                    self.done = True
            except Exception as e:
                print(log(True, f"Sync Error: {e}"))
        except Exception as e:
            await crash(e)
            print(log(True, f"Error occurred in starting up the self.bot!: {e}"))

    # prefix command error
    @commands.Cog.listener()
    async def on_command_error_event(self, ctx, error):
        await crash(error)
        embed = self.errorembed
        embed.add_field(name="Exception:", value=str(error))
        await ctx.reply(embed=embed, mention_author=False)

    # Slash command error
    @commands.Cog.listener()
    async def on_app_command_error_event(self, interaction, error):
        if str(error).startswith("The check functions for command "):
            return
        await crash(error)
        embed = self.errorembed
        embed.add_field(name="Exception:", value=str(error))
        try:
            await interaction.response.send_message(embed=embed)
        except discord.errors.InteractionResponded:
            await interaction.followup.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        channels = await guild.fetch_channels()
        embed = discord.Embed(title=f"Thanks for inviting {self.bot.user.display_name}!",
                              description=f"To get started, run </serverconfig:1400176415638556684> for your server configuration and </xpconfig:1467585730837479436> for the XP configuration both setup!\nYou may also use </help:1402434849154924665> to get help for commands! (* in the command parameter to get a list of all commands)\n-# **Guild Count: {len(self.bot.guilds)}**",
                              color=discord.Color.brand_green())
        embed.set_footer(text=guild.name + " | " + str(guild.id), icon_url=guild.icon.url if guild.icon else None)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url)
        embed.timestamp = datetime.now()

        for channel in channels:
            if isinstance(channel, discord.TextChannel):
                try:
                    await channel.send(embed=embed)
                    break
                except:
                    continue

    @commands.Cog.listener()
    async def on_guild_update(self, old: discord.Guild, new: discord.Guild):
        embed = discord.Embed(color=discord.Color.yellow())
        embed.set_author(name="Guild Update", icon_url=old.icon.url if old.icon else None)
        summary = []
        # TODO make this better eventually (not 13 if statements)
        if old.banner != new.banner:
            summary.append("- Server Banner Updated")
            embed.set_image(url=new.banner.url if new.banner else None)
            embed.add_field(name="Banner Update:", value=f"{old.banner.url if old.banner else None} -> {new.banner.url if new.banner else None}"[:1024])
        if old.description != new.description:
            summary.append("- Server Description Updated")
            embed.add_field(name="Description Update:", value=f"{old.description} -> {new.description}"[:1024])
        if old.dm_spam_detected_at != new.dm_spam_detected_at:
            summary.append("- DM Spam Detected")
            embed.add_field(name="DM Spam Detected:", value="At" + toDiscordTimestamp(new.dm_spam_detected_at, "R") if new.dm_spam_detected_at else None)
        if old.nsfw_level != new.nsfw_level:
            summary.append("- NSFW Level Updated")
            embed.add_field(name="NSFW Level Update:", value=f"{old.nsfw_level.name.capitalize()} -> {new.nsfw_level.name.capitalize()}")
        if old.icon != new.icon:
            summary.append("- Server Icon Updated")
            embed.add_field(name="Icon Updated:", value=f"{old.icon.url if old.icon else None} -> {new.icon.url if new.icon else None}"[:1024])
        if old.name != new.name:
            summary.append("- Server Name Updated")
            embed.add_field(name="Name Updated:", value=f"{old.name} -> {new.name}")
        if old.mfa_level != new.mfa_level:
            summary.append("- Moderator MFA Requirement Updated")
            embed.add_field(name="Mod MFA Requirement Update:", value=f"{old.mfa_level.name.capitalize().strip("_")} -> {new.mfa_level.name.capitalize().strip("_")}")
        if old.owner != new.owner:
            summary.append("- Server Owner Changed")
            embed.add_field(name="Owner Update:", value=f"{old.owner.mention} ({old.owner_id}) -> {new.owner.mention} ({new.owner_id}")
        if old.raid_detected_at != new.raid_detected_at:
            summary.append("- Server Raid Detected")
            embed.add_field(name="Server Raid:", value="At" + toDiscordTimestamp(new.raid_detected_at, "R"))
        if old.vanity_url != new.vanity_url:
            summary.append("- Vanity URL Updated")
            embed.add_field(name="Vanity URL Update", value=f"{old.vanity_url} -> {new.vanity_url}")
        if old.verification_level != new.verification_level:
            summary.append("- Member Verification Level Updated")
            embed.add_field(name="Verification Level Update:", value=f"{old.verification_level.name.capitalize()} -> {new.verification_level.name.capitalize()}")

        if not embed.fields or not summary:
            return
        embed.description = "\n".join(summary)
        await event(self.bot, new, "guild", new, embed)

    # <editor-fold desc="Member Events">
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        temp = discord.Embed(description=f"{member.mention} {member.name}", color=discord.Color.brand_green())
        temp.set_author(name="Member Joined", icon_url=member.avatar.url if member.avatar else None)
        temp.add_field(name="Account Created:", value=f"<t:{int(member.created_at.timestamp())}:R>")
        temp.add_field(name="Member Count:", value=guild.member_count)
        await event(self.bot, guild, "member", member, temp)
        embed = discord.Embed(color=discord.Color.brand_green())
        for gid, _ in custom_urls.items():
            if guild.id == gid:
                embed.set_image(url=custom_urls[guild.id]["welcome"])
        if guild.id == 1373049145572593784:
            channel = self.bot.get_channel(1373060852558598276)
            emoji = self.bot.get_emoji(1415121249822179419)
            msg = await channel.send(
                f"Hello, ⁜{member.mention}※ and welcome to **Whispers of Robloxia! [WOR]** hope you enjoy.\nPlease look at <#1373059418845085817> so you understand what to do and not to do thank you!",
                embed=embed)
            await msg.add_reaction(emoji)
        elif guild.id == 1418384480061624444:
            await self.bot.get_channel(1418384488098037771).send(
                f"Welcome to Stop N' Go, {member.mention}!! I hope you enjoy your stop :D",
                allowed_mentions=discord.AllowedMentions(users=False))
        elif guild.id == 1489081230455476246:
            channel = self.bot.get_channel(1489096330495397989)
            await channel.send(f"{member.mention} has joined! Make sure to punch Partygoer on your way in, and watch out for edgy maniacs with hacks.\nWe are now at {guild.member_count} members.")
        elif guild.id == 1501806820254285905:
            role = member.guild.get_role(1501860189291155476)
            await member.add_roles(role)
            

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        roles = [r.mention for r in member.roles if not r.is_default()]
        temp = discord.Embed(description=f"{member.mention} {member.name}", color=discord.Color.brand_red())
        temp.set_author(name="Member Left", icon_url=member.avatar.url if member.avatar else None)
        temp.add_field(name="Account Created:", value=f"<t:{int(member.created_at.timestamp())}:R>")
        temp.add_field(name="Member Count:", value=guild.member_count)
        temp.add_field(name="Roles:", value="\n".join(roles) if roles else "No roles.")
        await event(self.bot, guild, "member", member, temp)
        embed = discord.Embed(color=discord.Color.brand_red())
        for gid, _ in custom_urls.items():
            if guild.id == gid:
                embed.set_image(url=custom_urls[guild.id]["goodbye"])
        if guild.id == 1373049145572593784:
            channel = self.bot.get_channel(1373060852558598276)
            emoji = self.bot.get_emoji(1386741952040407112)
            msg = await channel.send(
                f"aw geez {member.mention} has left us... We are now {guild.member_count} friends :,<", embed=embed)
            await msg.add_reaction(emoji)
        elif guild.id == 1418384480061624444:
            await self.bot.get_channel(1418384488098037771).send(
                f"Oh...goodbye, {member.mention}...you have stopped and gone....",
                allowed_mentions=discord.AllowedMentions(users=False))
        elif guild.id == 1489081230455476246:
            channel = self.bot.get_channel(1489096330495397989)
            await channel.send(f"{member.mention} couldn't evade a ban. Well, they aren't BANNED, they just left and this is a humorous leave message due to the name of the game.\nWe are now at {guild.member_count} members.")

    @commands.Cog.listener()
    async def on_member_update(self, old: discord.Member, new):
        embed = discord.Embed(colour=discord.Colour.yellow())
        embed.set_author(name=new.name, icon_url=new.avatar.url if new.avatar else None)
        summary = new.mention + " has been updated:\n"
        oldroles = [r.mention for r in old.roles if not r.is_default()]
        newroles = [r.mention for r in new.roles if not r.is_default()]
        added = []
        removed = []
        for role in oldroles:
            if not role in newroles:
                removed.append(role)
        for role in newroles:
            if not role in oldroles:
                added.append(role)

        if not added == []:
            summary += "- Roles Added\n"
            embed.add_field(name="Roles Added:", value=", ".join(added))
        if not removed == []:
            summary += "- Roles Removed\n"
            embed.add_field(name="Roles Removed:", value=", ".join(removed))
        if not old.nick == new.nick:
            summary += "- Nickname Changed\n"
            embed.add_field(name="Nickname Changed:", value=f"Before: {old.nick} | After: {new.nick}")
        if not old.timed_out_until == new.timed_out_until:
            summary += "- Timeout Updated\n"
            embed.add_field(name="Timeout Updated",
                            value=f"Before: {f"<t:{int(old.timed_out_until.timestamp())}:f>" if old.timed_out_until else None} | After: {f"<t:{int(new.timed_out_until.timestamp())}:f>" if new.timed_out_until else None}")
        if not old.premium_since == new.premium_since:
            if old.premium_since is None:
                summary += "- Started server boosting\n"
            else:
                summary += f"- Stopped server boosting (Started boosting at <t:{int(new.premium_since.timestamp())}:d>)\n"
        embed.description = summary

        if summary == new.mention + " has been updated:\n":
            return
        await event(self.bot, new.guild, "member", new, embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        user = self.bot.get_user(user.id)  # getting discord.User just in case event sends discord.Member
        embed = discord.Embed(color=discord.Colour.brand_red())
        embed.set_author(name="Member Banned", icon_url=user.avatar.url if user.avatar else None)
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        embed.description = f"{user.mention} {user.name}"

        await event(self.bot, guild, "member", user, embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        user = self.bot.get_user(user.id)  # getting discord.User just in case event sends discord.Member
        embed = discord.Embed(color=discord.Colour.brand_green())
        embed.set_author(name="Member Unbanned", icon_url=user.avatar.url if user.avatar else None)
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        embed.description = f"{user.mention} {user.name}"

        await event(self.bot, guild, "member", user, embed)

    # </editor-fold>

    # <editor-fold desc="Message Events">
    @commands.Cog.listener()
    async def on_message_edit(self, old: discord.Message, new: discord.Message):
        if old.author == self.bot.user:
            return
        if old.content == new.content:
            return
        bannedword = next(
            (word for word in server_settings(False, new.guild, "banned") if re.search(rf"\b{re.escape(word)}\b", new.content.strip(), re.IGNORECASE)),
            None)
        if bannedword and (not permCheck(new.guild, new.author) or new.guild.id == 1373049145572593784):
            await new.delete(delay=0)
            embed = discord.Embed(
                description=f"Message Content:\n{new.content.lower().replace(bannedword, f"**{bannedword}**")[:4079]}",
                color=discord.Color.yellow())
            embed.set_author(name="FLAGGED WORD", icon_url=new.author.avatar.url if new.author.avatar else None)
            embed.add_field(name="User:", value=new.author.mention)
            embed.add_field(name="Channel:", value=new.channel.mention)
            embed.add_field(name="Surrounding:",value=[msg async for msg in new.channel.history(limit=1, before=new.created_at)][-1].jump_url)
            embed.add_field(name="Banned Word:", value=bannedword)
            embed.set_footer(text=f"User ID: {new.author.id}")
            await event(self.bot, new.guild, "modlog", None, embed)
            await new.channel.send(
                f"{new.author.mention}, your message had a flagged word! Please be careful of what you say.\n-# Banned Word: {bannedword}",
                delete_after=6)
            return
        embed = discord.Embed(description=f"Message edited in {old.channel.mention}\n[Jump to Message]({old.jump_url})",
                              colour=discord.Colour.brand_green())
        embed.set_author(name=old.author.name, icon_url=old.author.avatar.url if old.author.avatar else None)
        embed.add_field(name="Before:",
                        value=f"{old.content[:1021]}{"..." if len(old.content) >= 1024 else old.content[1022:1024]}")
        embed.add_field(name="After:",
                        value=f"{new.content[:1021]}{"..." if len(new.content) >= 1024 else old.content[1022:1024]}")
        await event(self.bot, old.guild, "message", old, embed)

    @commands.Cog.listener()
    async def on_message_delete(self, msg: discord.Message):
        if msg.author == self.bot.user or msg.author.name == "ABotmo Logs":
            return
        embed = discord.Embed(title=f"Message deleted in {msg.channel.mention}", description=msg.content,
                              colour=discord.Colour.brand_red())
        embed.set_author(name=msg.author.name, icon_url=msg.author.avatar.url if msg.author.avatar else None)
        if not msg.attachments == []:
            stuff = [a.filename for a in msg.attachments]
            embed.add_field(name="Attachments:", value=",\n".join(stuff))
            file = msg.attachments[0]
            if len(msg.attachments) == 1 and file.content_type.find("image") > -1:
                embed.set_image(url=file.proxy_url)
        await event(self.bot, msg.guild, "message", msg, embed)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, msgs):
        first = msgs[0]
        thing = []
        for msg in msgs:
            thing.append(f"{msg.author.mention}: {msg.content[:30]}{"..." if len(msg.content) >= 30 else ""}")
        embed = discord.Embed(title=f"Bulk Delete in {first.channel.mention}",
                              description=f"**{len(msgs)} messages deleted.**\n{"\n".join(thing)}", color=discord.Color.brand_red())
        embed.set_author(name=first.guild.name, icon_url=first.guild.icon.url if first.guild.icon else None)

        await event(self.bot, first.guild, "message", first.channel, embed)

    # </editor-fold>

    # <editor-fold desc="Role Events">
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        embed = discord.Embed(description=f"Role Created: {role.name} ({role.mention})", color=role.color)
        embed.set_author(name=role.guild.name, icon_url=role.guild.icon.url if role.guild.icon else None)
        perms = []
        for name, value in iter(role.permissions):
            if value:
                perms.append(name.replace('_', ' ').title())

        embed.add_field(name="Hoisted:", value=role.hoist)
        embed.add_field(name="Mentionable:", value=role.mentionable)
        if not perms == []:
            embed.add_field(name="Permissions:", value=", ".join(perms))

        await event(self.bot, role.guild, "role", role, embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        embed = discord.Embed(description=f"Role Deleted: {role.name}", color=discord.Color.brand_red())
        embed.set_author(name=role.guild.name, icon_url=role.guild.icon.url if role.guild.icon else None)
        perms = []
        for name, value in iter(role.permissions):
            if value:
                perms.append(name.replace('_', ' ').title())

        embed.add_field(name="Hoisted:", value=role.hoist)
        embed.add_field(name="Mentionable:", value=role.mentionable)
        if not perms == []:
            embed.add_field(name="Permissions:", value=", ".join(perms))

        await event(self.bot, role.guild, "role", role, embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, old, new):
        embed = discord.Embed(title=f"Role Updated: {old.name}", description=f"{new.mention} was updated:",
                              color=new.color)
        embed.set_author(name=new.guild.name, icon_url=new.guild.icon.url if new.guild.icon else None)
        oldperms = []
        newperms = []
        change = False
        for name, value in iter(old.permissions):
            if value:
                oldperms.append(name.replace('_', ' ').title())
        for name, value in iter(new.permissions):
            if value:
                newperms.append(name.replace('_', ' ').title())

        removed = []
        added = []
        for perm in oldperms:
            if not perm in newperms:
                added.append(perm)
        for perm in newperms:
            if not perm in oldperms:
                removed.append(perm)

        if not old.name == new.name:
            embed.add_field(name="Name Changed:", value=f"{old.name} -> {new.name}")
            change = True
        if not removed == []:
            embed.add_field(name="Added Permissions:", value=", ".join(removed))
            change = True
        if not added == []:
            embed.add_field(name="Removed Permissions:", value=", ".join(added))
            change = True
        if not old.hoist == new.hoist:
            embed.add_field(name="Hoisted:", value=new.hoist)
            change = True
        if not old.mentionable == new.mentionable:
            embed.add_field(name="Mentionable", value=new.mentionable)
            change = True
        if not old.color == new.color:
            embed.add_field(name="Color:", value=f"{str(old.color)} -> {str(new.color)}")
            change = True

        if not change:
            return

        await event(self.bot, new.guild, "role", new, embed)

    # </editor-fold>

    # <editor-fold desc="Channel Events">
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        embed = discord.Embed(color=discord.Color.brand_green())
        if channel.type == discord.ChannelType.category:
            embed.description = f"**Category Created**: {channel.name}\n**Position**: {channel.position}"
            embed.set_author(name=channel.guild.name, icon_url=channel.guild.icon.url if channel.guild.icon else None)
        else:
            embed.description = f"**Channel Created**: {channel.name} ({channel.mention})\n**Category**: {channel.category}\n**Channel Type**: {str(channel.type).capitalize()}"
            embed.set_author(name=channel.guild.name, icon_url=channel.guild.icon.url if channel.guild.icon else None)

        await event(self.bot, channel.guild, "channel", channel, embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        embed = discord.Embed(color=discord.Color.brand_red())
        if channel.type == discord.ChannelType.category:
            embed.description = f"**Category Deleted**: {channel.name}\n**Position**: {channel.position}"
            embed.set_author(name=channel.guild.name, icon_url=channel.guild.icon.url if channel.guild.icon else None)
        else:
            embed.description = f"**Channel Deleted**: {channel.name}\n**Category**: {channel.category}\n**Channel Type**: {str(channel.type).capitalize()}"
            embed.set_author(name=channel.guild.name, icon_url=channel.guild.icon.url if channel.guild.icon else None)

        await event(self.bot, channel.guild, "channel", channel, embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, old, new):
        embed = discord.Embed(
            title=f"{"Channel" if not old.type == discord.ChannelType.category else "Category"} Updated: {old.name} ({str(old.type).capitalize()})",
            description=f"{new.mention} was changed:\n\n", colour=discord.Color.yellow())
        embed.set_author(name=new.guild.name, icon_url=new.guild.icon.url if new.guild.icon else None)
        oldow = old.overwrites
        newow = new.overwrites
        oldkeys = set(oldow.keys())
        newkeys = set(newow.keys())
        change = False

        if not old.name == new.name:
            embed.description += f"Name Changed: {old.name} -> {new.name}\n"
            change = True
        if not old.category.id == new.category.id:
            embed.description += f"Category changed: {old.category.name} -> {new.category.name}\n"
            change = True

        for target in newkeys - oldkeys:
            embed.add_field(name="Overwrite Added", value=target.mention if hasattr(target, "mention") else target.name)
            change = True

        for target in oldkeys - newkeys:
            embed.add_field(name="Overwrite Removed",
                            value=target.mention if hasattr(target, "mention") else target.name)
            change = True

        for target in oldkeys & newkeys:
            oldperm = oldow[target]
            newperm = newow[target]
            changes = []

            for perm, oldval in oldperm:
                newval = getattr(newperm, perm)
                if not oldval == newval:
                    changes.append(f"- **{perm.replace("_", " ").title()}**: {oldval} -> {newval}")

            if changes:
                embed.description += f"Permissions Changed for {target.mention if hasattr(target, "mention") else target.name}:\n{"\n".join(changes)}"
                change = True

        if not change:
            return

        await event(self.bot, new.guild, "channel", old, embed)

    # </editor-fold>

    # <editor-fold desc="Voice Events">
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, old, new):
        embed = discord.Embed(color=discord.Color.yellow())
        embed.set_author(name=member.name, icon_url=member.avatar.url if member.avatar else None)
        things = []
        if not old.channel == new.channel:
            if old.channel is None:
                things.append(f"Joined VC Channel: {new.channel.mention}")
            elif new.channel is None:
                things.append(f"Left VC Channel: {old.channel.mention}")
            else:
                things.append(f"Moved VCs: {old.channel.mention} -> {new.channel.mention}")
        if not old.mute == new.mute:
            things.append(f"Is {"now" if new.mute else "no longer"} Server Muted")
        if not old.deaf == new.deaf:
            things.append(f"Is {"now" if new.deaf else "no longer"} Server Deafened")

        if not things:
            return

        embed.description = f"{member.mention} {", ".join(things)}"

        await event(self.bot, member.guild, "voice", new.channel or old.channel, embed)

    # </editor-fold>

    # On message events
    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot:
            return

        guild = msg.guild
        user = msg.author
        if guild:
            if msg.channel.id in [1520670426379063327, 1520671235560837120]: await user.ban(delete_message_days=7, reason="Sending message into anti-self-bot channel"); return;
            bannedlist: list = server_settings(False, guild, "banned")
            bannedword = next((word for word in bannedlist if re.search(rf"\b{re.escape(word)}\b", msg.content.strip(), re.IGNORECASE)),None)
            if guild.id == 1373049145572593784:
                link = re.findall(r'https?://\S+', msg.content.strip(), re.IGNORECASE)
                gg = re.findall(r'.gg/\S+', msg.content.strip(), re.IGNORECASE)
                invite = re.findall(r'/invite/\S+', msg.content.strip(), re.IGNORECASE)
                if not guild.get_member(user.id).guild_permissions.embed_links and (link or gg or invite):
                    chosen = link or gg or invite
                    channel = msg.channel
                    await msg.delete(delay=0)
                    await channel.send(f"{user.mention}, you can not send suspicious links here unless you have the \"Embed Links\" permission!", delete_after=8)
                    embed = discord.Embed(
                        description=f"Message Content:\n{msg.content}", color=discord.Color.yellow())
                    embed.set_author(name="FLAGGED LINK(S)", icon_url=user.avatar.url if user.avatar else None)
                    embed.add_field(name="User:", value=user.mention)
                    embed.add_field(name="Channel:", value=msg.channel.mention)
                    embed.add_field(name="Surrounding:", value=[msg async for msg in msg.channel.history(limit=1, before=msg.created_at)][-1].jump_url)
                    embed.add_field(name="Banned Link(s):", value=", ".join(chosen))
                    embed.set_footer(text=f"User ID: {user.id}")
                    await event(self.bot, guild, "modlog", None, embed)
                    return
            if bannedword and (not permCheck(guild, user) or guild.id == 1373049145572593784):
                await msg.delete(delay=0)
                embed = discord.Embed(description=f"Message Content:\n{msg.content.lower().replace(bannedword, f"**{bannedword}**")[:4079]}", color=discord.Color.yellow())
                embed.set_author(name="FLAGGED WORD", icon_url=user.avatar.url if user.avatar else None)
                embed.add_field(name="User:", value=user.mention)
                embed.add_field(name="Channel:", value=msg.channel.mention)
                embed.add_field(name="Surrounding:", value=[msg async for msg in msg.channel.history(limit=1, before=msg.created_at)][-1].jump_url)
                embed.add_field(name="Banned Word:", value=bannedword)
                embed.set_footer(text=f"User ID: {user.id}")
                await event(self.bot, guild, "modlog", None, embed)
                await msg.channel.send(f"{user.mention}, your message had a flagged word! Please be careful of what you say.\n-# Banned Word: {bannedword}", delete_after=6)
                return
            if msg.content.startswith(await get_prefix(None, msg)):
                return
            data = xp_settings(False, guild, None)
            if data["xpenabled"]:
                lvl_up, lvl = xp(True, guild, int(time.time()), user)

                if lvl_up:
                    role = xp_roles(False, guild, lvl)
                    try:
                        if not role is None:
                            role = guild.get_role(int(role))
                            if not role is None:
                                await user.add_roles(role, reason=f"Level up to {lvl}")
                        if data["messagetoggle"]:
                            if data["channel"] == 1:
                                    await msg.reply(
                                    f"{msg.author.mention}, you have succesfully leveled up to Level {lvl}{f", and got the role {role.mention}" if role else ""}!",
                                        allowed_mentions=noMentions)
                            else:
                                channel = msg.guild.get_channel(data["channel"])
                                if discord.app_commands.checks.bot_has_permissions(attach_files=True):
                                    await channel.send(f"{msg.author.mention} has successfully leveled up to Level {lvl}{f", and got the role {role.mention}" if role else ""}!", file=discord.File(fp=levelCard(lvl, msg.author.avatar), filename="lvlup.png"), allowed_mentions=noRoleMentions)
                                else:
                                    await channel.send(
                                    f"{msg.author.mention} has successfully leveled up to Level {lvl}{f", and got the role {role.mention}" if role else ""}", allowed_mentions=noRoleMentions)
                        else:
                            enabled = user_settings(False, user.id, "xpmessage")
                            if enabled:
                                if enabled == 2:
                                    await user.send(
                                        f"You have succesfully leveled up to Level {lvl} in {guild.name} ({guild.id}){f", and got the role {role.name}" if role else ""}!{"\n-# *You can toggle this message with /settings!*" if lvl % 5 == 0 else ""}")
                                else:
                                    await msg.reply(
                                            f"{msg.author.mention}, you have succesfully leveled up to Level {lvl}{f", and got the role {role.mention}" if role else ""}!{"\n-# *You can toggle this message with /settings!*" if lvl % 5 == 0 else ""}",
                                            allowed_mentions=noRoleMentions)
                    except Exception as e:
                        print(log(True, f"on_message raised an error: " + str(e)))
                        pass

        await self.bot.process_commands(msg)

async def setup(bot):
    await bot.add_cog(Events(bot))

async def load(bot):
    await bot.load_extension("Cogs.BotEvents")