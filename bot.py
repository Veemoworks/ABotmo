import discord, os, platform, sys, logging
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
from Cogs.Methods.methods import crash
from Cogs.Methods.asynchronous.botEvents import command_error, app_command_error, message
from Cogs.Methods.asynchronous.botStatus import status, kuma, ramthing
from Cogs.Methods.asynchronous.methods import get_prefix, event
from Cogs.Methods.methods import handle_exception, log, close_bot
from resources.dictionaries import custom_urls

# Variables
version = "0.6.14"
pid = os.getpid()
debugging = False
done = False
startup = datetime.now()

# Load .env, clear old output.txt, and initalize the bot
load_dotenv()
with open("output.txt", "w") as f:
    f.write("")
    print(log(False, "Initilizaing..."))
if debugging:
    with open("debug.txt", "w") as f:
        f.write("")
bot = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.all(), max_messages=500)

# Bot event for when bot starts up
@bot.event
async def on_ready():
    global done
    try:
        try:
            if not done:
                # Load cogs
                cogs = ["fun", "utils", "moderation", "server", "prefix.utils", "prefix.server"]
                for cog in cogs:
                    await bot.load_extension(f"commands.{cog}")
                # Sync bot tree.
                synced = await bot.tree.sync()
                now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                thing = (f"\033[92m[{now}] [INFO    ] ABotmo v{version}\n"
                         f"[{now}] [INFO    ] Logged in as {bot.user}\n"
                         f"[{now}] [INFO    ] discord.py V{discord.__version__}\n"
                         f"[{now}] [INFO    ] Python {platform.python_version()}\n"
                         f"[{now}] [INFO    ] Running on: {platform.system()} {platform.release()} ({os.name})\n"
                         f"[{now}] [INFO    ] Synced {len(synced)} commands\n"
                         f"[{now}] [INFO    ] Registering new commands from: {", ".join(cogs)}.\n"
                )
                print(thing, end="")
                with open("output.txt", "a") as r:
                    r.write(thing.removeprefix("\033[92m"))
                cmds = await bot.tree.fetch_commands()
                for command in cmds:
                    print(log(False, f"Command {command.name} (</{command.name}:{command.id}>) Registered!"))
                # Bot Loops
                ramthing.start()
                status.start(bot)
                kuma.start(bot)
                t = bot.get_channel(1403041372751265912)
                await t.edit(name="Bot Status: ✅")
                print(log(False, f"READY TO KILL ALL FELLAS..."))
                done = True
        except Exception as e:
            print(log(True, f"Sync Error: {e}"))
    except Exception as e:
        await crash(e)
        print(log(True,f"Error occurred in starting up the bot!: {e}"))

# prefix command error
@bot.event
async def on_command_error_event(ctx, error):
    await command_error(ctx, error)

# Slash command error
@bot.tree.error
async def on_app_command_error_event(interaction, error):
    await app_command_error(interaction, error)

@bot.event
async def on_guild_join(guild: discord.Guild):
    channels = await guild.fetch_channels()
    embed = discord.Embed(title=f"Thanks for inviting {bot.user.display_name}!", description=f"To get started, run </serverconfig:1400176415638556684> for your server configuration and </xpconfig:1467585730837479436> for the XP configuration both setup!\nYou may also use </help:1402434849154924665> to get help for commands! (* in the command parameter to get a list of all commands)\n-# **Guild Count: {len(bot.guilds)}**", color=discord.Color.brand_green())
    embed.set_footer(text=guild.name + " | " + str(guild.id), icon_url=guild.icon.url if guild.icon else None)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.set_author(name=bot.user.display_name, icon_url=bot.user.avatar.url)
    embed.timestamp = datetime.now()

    for channel in channels:
        if isinstance(channel, discord.TextChannel):
            try:
                await channel.send(embed=embed)
                break
            except:
                continue

# <editor-fold desc="Member Events">
@bot.event
async def on_member_join(member):
    guild = member.guild
    temp = discord.Embed(description=f"{member.mention} {member.name}", color=discord.Color.brand_green())
    temp.set_author(name="Member Joined", icon_url=member.avatar.url)
    temp.add_field(name="Account Created:", value=f"<t:{int(member.created_at.timestamp())}:R>")
    await event(bot, guild, "member", member, temp)
    embed = discord.Embed(color=discord.Color.brand_green())
    for gid, _ in custom_urls.items():
        if guild.id == gid:
            embed.set_image(url=custom_urls[guild.id]["welcome"])
    if guild.id == 1373049145572593784:
        channel = bot.get_channel(1373060852558598276)
        emoji = bot.get_emoji(1415121249822179419)
        msg = await channel.send(f"Hello, ⁜{member.mention}※ and welcome to **Whispers of Robloxia! [WOR]** hope you enjoy.\nPlease look at <#1373059418845085817> so you understand what to do and not to do thank you!", embed=embed)
        await msg.add_reaction(emoji)
    elif guild.id == 1418384480061624444:
        await bot.get_channel(1418384488098037771).send(f"Welcome to Stop N' Go, {member.mention}!! I hope you enjoy your stop :D", allowed_mentions=discord.AllowedMentions(users=False))

@bot.event
async def on_member_remove(member):
    guild = member.guild
    roles = [r.mention for r in member.roles if not r.is_default()]
    temp = discord.Embed(description=f"{member.mention} {member.name}", color=discord.Color.brand_red())
    temp.set_author(name="Member Left", icon_url=member.avatar.url)
    temp.add_field(name="Account Created:", value=f"<t:{int(member.created_at.timestamp())}:R>")
    temp.add_field(name="Roles:", value="\n".join(roles) if roles else "No roles.")
    await event(bot, guild, "member", member, temp)
    embed = discord.Embed(color=discord.Color.brand_red())
    for gid, _ in custom_urls.items():
        if guild.id == gid:
            embed.set_image(url=custom_urls[guild.id]["goodbye"])
    if guild.id == 1373049145572593784:
        channel = bot.get_channel(1373060852558598276)
        emoji = bot.get_emoji(1386741952040407112)
        msg = await channel.send(f"aw geez {member.mention} has left us... We are now {guild.member_count} friends :,<", embed=embed)
        await msg.add_reaction(emoji)
    elif guild.id == 1418384480061624444:
        await bot.get_channel(1418384488098037771).send(f"Oh...goodbye, {member.mention}...you have stopped and gone....", allowed_mentions=discord.AllowedMentions(users=False))

@bot.event
async def on_member_update(old, new):
    embed = discord.Embed(colour=discord.Colour.yellow())
    embed.set_author(name=new.name, icon_url=new.avatar.url)
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
        embed.add_field(name="Timeout Updated", value=f"Before: {f"<t:{int(old.timed_out_until.timestamp())}:f>" if old.timed_out_until else None} | After: {f"<t:{int(new.timed_out_until.timestamp())}:f>" if new.timed_out_until else None}")
    embed.description = summary

    if summary == new.mention + " has been updated:\n":
        return
    await event(bot, new.guild, "member", new, embed)

@bot.event
async def on_member_ban(guild, user):
    user = bot.get_user(user.id) # getting discord.User just in case event sends discord.Member
    embed = discord.Embed(color=discord.Colour.brand_red())
    embed.set_author(name="Member Banned", icon_url=user.avatar.url)
    embed.set_thumbnail(url=user.avatar.url)
    embed.description = f"{user.mention} {user.name}"

    await event(bot, guild, "member", user, embed)

@bot.event
async def on_member_unban(guild, user):
    user = bot.get_user(user.id)  # getting discord.User just in case event sends discord.Member
    embed = discord.Embed(color=discord.Colour.brand_green())
    embed.set_author(name="Member Unbanned", icon_url=user.avatar.url)
    embed.set_thumbnail(url=user.avatar.url)
    embed.description = f"{user.mention} {user.name}"

    await event(bot, guild, "member", user, embed)
# </editor-fold>

# <editor-fold desc="Message Events">
@bot.event
async def on_message_edit(old, new):
    if old.content == new.content:
        return
    embed = discord.Embed(description=f"Message edited in {old.channel.mention}\n[Jump to Message]({old.jump_url})", colour=discord.Colour.brand_green())
    embed.set_author(name=old.author.name, icon_url=old.author.avatar.url)
    embed.add_field(name="Before:", value=old.content[:1024])
    embed.add_field(name="After:", value=new.content[:1024])

    await event(bot, old.guild, "message", old, embed)

@bot.event
async def on_message_delete(msg: discord.Message):
    embed = discord.Embed(title=f"Message deleted in {msg.channel.mention}", description=msg.content, colour=discord.Colour.brand_red())
    embed.set_author(name=msg.author.name, icon_url=msg.author.avatar.url)
    if not msg.attachments == []:
        stuff = [a.filename for a in msg.attachments]
        embed.add_field(name="Attachments:", value=", ".join(stuff))
        file = msg.attachments[0]
        if len(msg.attachments) == 1 and file.content_type.find("image") > -1:
            embed.set_image(url=file.proxy_url)
    await event(bot, msg.guild, "message", msg, embed)

@bot.event
async def on_bulk_message_delete(msgs):
    first = msgs[0]
    embed = discord.Embed(title=f"Bulk Delete in {first.channel.mention}", description=f"**{len(msgs)} messages deleted.**", color=discord.Color.brand_red())
    embed.set_author(name=first.guild.name, icon_url=first.guild.icon.url if first.guild.icon else None)

    await event(bot, first.guild, "message", first.channel, embed)

# </editor-fold>

# <editor-fold desc="Role Events">
@bot.event
async def on_guild_role_create(role):
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

    await event(bot, role.guild, "role", role, embed)

@bot.event
async def on_guild_role_delete(role):
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

    await event(bot, role.guild, "role", role, embed)

@bot.event
async def on_guild_role_update(old, new):
    embed = discord.Embed(title=f"Role Updated: {old.name}", description=f"{new.mention} was updated:", color=new.color)
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
        embed.add_field(name="Name Changed:" , value=f"{old.name} -> {new.name}")
        change = True
    if not removed == []:
        embed.add_field(name="Removed Permissions:", value=", ".join(removed))
        change = True
    if not added == []:
        embed.add_field(name="Added Permissions:", value=", ".join(added))
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

    await event(bot, new.guild, "role", new, embed)

# </editor-fold>

# <editor-fold desc="Channel Events">
@bot.event
async def on_guild_channel_create(channel):
    embed = discord.Embed(color=discord.Color.brand_green())
    if channel.type == discord.ChannelType.category:
        embed.description = f"**Category Created**: {channel.name}\n**Position**: {channel.position}"
        embed.set_author(name=channel.guild.name, icon_url=channel.guild.icon.url if channel.guild.icon else None)
    else:
        embed.description = f"**Channel Created**: {channel.name} ({channel.mention})\n**Category**: {channel.category}\n**Channel Type**: {str(channel.type).capitalize()}"
        embed.set_author(name=channel.guild.name, icon_url=channel.guild.icon.url if channel.guild.icon else None)

    await event(bot, channel.guild, "channel", channel, embed)

@bot.event
async def on_guild_channel_delete(channel):
    embed = discord.Embed(color=discord.Color.brand_red())
    if channel.type == discord.ChannelType.category:
        embed.description = f"**Category Deleted**: {channel.name}\n**Position**: {channel.position}"
        embed.set_author(name=channel.guild.name, icon_url=channel.guild.icon.url if channel.guild.icon else None)
    else:
        embed.description = f"**Channel Deleted**: {channel.name}\n**Category**: {channel.category}\n**Channel Type**: {str(channel.type).capitalize()}"
        embed.set_author(name=channel.guild.name, icon_url=channel.guild.icon.url if channel.guild.icon else None)

    await event(bot, channel.guild, "channel", channel, embed)

@bot.event
async def on_guild_channel_update(old, new):
    embed = discord.Embed(title=f"{"Channel" if not old.type == discord.ChannelType.category else "Category"} Updated: {old.name} ({str(old.type).capitalize()})", description=f"{new.mention} was changed:\n\n",colour=discord.Color.yellow())
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
        embed.add_field(name="Overwrite Removed", value=target.mention if hasattr(target, "mention") else target.name)
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

    await event(bot, new.guild, "channel", old, embed)

# </editor-fold>

# <editor-fold desc="Voice Events">
@bot.event
async def on_voice_state_update(member, old, new):
    embed = discord.Embed(color=discord.Color.yellow())
    embed.set_author(name=member.name, icon_url=member.avatar.url)
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

    await event(bot, member.guild, "voice", new.channel or old.channel, embed)
# </editor-fold>

# On message events
@bot.event
async def on_message(msg):
    await message(msg)

    await bot.process_commands(msg)

# System exception
sys.excepthook = handle_exception

# Run bot
if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"), log_handler=logging.FileHandler(filename='debug.txt', encoding='utf-8', mode='a') if debugging else None, log_level=logging.DEBUG)
    close_bot()
