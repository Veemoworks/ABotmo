import discord, json, random
from discord import app_commands
from discord.ext import commands
from Cogs.Methods.methods import log, to_text, canUse, xpEnabledOnly
from Cogs.Classes.DiscordViews import Config, XPConfig
from resources.dictionaries import setting_users
from DataBases.database import xp, server_settings, user_settings, xp_settings, server_channels, nextLevel, xp_roles


class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverconfig", description="Change the configuration of the server for the bot.")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    async def serverconfig(self, interaction: discord.Interaction):
        print(log(False,
                  f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id} ({interaction.guild.name})!"))
        await interaction.response.defer(ephemeral=True)
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("You do not have permission to run this command!")
            return
        currconfig = server_settings(False, interaction.guild, None)
        currconfig = currconfig | server_channels(False, interaction.guild, None)
        currconfig.pop("casenum")
        val = currconfig.pop("channel")
        currconfig["mchannel"] = val
        embed = discord.Embed(
            title="Server Configuration",
            description=f"Welcome to the Server Configuration Panel, {interaction.user.mention}!\n"
                        "Only Administrators can access this menu.\n\n"
                        f"**__Current Config__**:\n{to_text(currconfig)}\n\n"
                        "Choose what you’d like to configure below:",
            color=discord.Color.brand_green()
        )
        view = Config(interaction)
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="xpconfig", description="Change the XP configuration of the server for the bot.")
    @app_commands.describe(message="Toggle if level up messages are sent", channel="Configure where level up messages are sent (select current one for Current Channel config)", cd="Configure the cooldown between each message before giving XP", xprange="Configure the range of random XP given", xpenabled="Toggle if XP should be enabled")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    async def xpconfig(self, interaction: discord.Interaction, message: bool = None, channel: discord.TextChannel = None, cd: int = None, xprange: str = None, xpenabled: bool = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id} ({interaction.guild.name})!"))
        # soon a module like serverconfig
        await interaction.response.defer(ephemeral=True)
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("You do not have permission to run this command!")
            return

        currconfig: dict = xp_settings(False, interaction.guild, None)
        currconfig["lroles"] = xp_roles(False, interaction.guild)
        if not currconfig["xpenabled"]:
            currconfig.clear()
            currconfig["xpenabled"] = 0
        embed = discord.Embed(title="XP Configuration", description=f"Welcome to the XP Configuration Panel, {interaction.user.mention}!\nOnly Administrators can access this command.\n\n**__Current Config:__**\n{to_text(currconfig, True)}\n\nYour changes will soon be adjusted, please wait...", color=discord.Color.brand_green())
        msg = await interaction.followup.send(embed=embed)
        embed.description = embed.description.removesuffix("Your changes will soon be adjusted, please wait...")
        if not xprange is None:
            success = False
            try:
                xprange = json.loads(f"[{xprange}]")
                if len(xprange) > 2 or len(xprange) < 2:
                    success = False
                    embed.description += "Please enter **2** numbers with a comma seperating them for xp range. (Example: '1, 25')\n"
                else:
                    if xprange[0] < 1 or xprange[1] < 1:
                        success = False
                        embed.description += "Input a number that is bigger than 0. (Example: `3, 60')\n"
                    else:
                        xprange = f"'{xprange}'"
                        success = True

            except json.decoder.JSONDecodeError:
                success = False
                embed.description += "Please enter **2 NUMBERS** with a comma seperating them for xp range. (Example: '1, 25')\n"

            if not success:
                await msg.edit(embed=embed)
                return
        if not cd is None:
            success = False
            if cd > 60:
                success = False
                embed.description += "Pleae enter a cool down of less than 60 seconds!\n"
            else:
                success = True
            if not success:
                await msg.edit(embed=embed)
                return
        if not channel is None:
            if channel.id == interaction.channel.id:
                channel = 1
            else:
                channel = channel.id
        temp = {
            "messagetoggle": message,
            "channel": channel,
            "cd": cd,
            "range": xprange,
            "xpenabled": xpenabled
        }
        data = {}
        for datatype, val in temp.items():
            if val is None:
                data[datatype] = [False, None]
            else:
                data[datatype] = [True, val]
        embed.description += xp_settings(True, interaction.guild, data) + f"\nChoose what you’d like to configure below:"

        view = XPConfig(interaction)
        await msg.edit(embed=embed, view=view)

    @app_commands.command(name="rank", description="Check your rank in this server!")
    @app_commands.describe(user="User to check")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    async def rank(self, interaction: discord.Interaction, user: discord.Member = None):
        print(log(False,f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id} ({interaction.guild.name})!"))
        has_perms = app_commands.checks.bot_has_permissions(embed_links=True)
        embed = discord.Embed(color=discord.Color.brand_green())
        await interaction.response.defer()

        if not server_settings(False, interaction.guild, "xpenabled"):
            if has_perms:
                embed.set_author(name="This server has XP disabled!", icon_url=interaction.guild.icon.url)
                await interaction.followup.send(embed=embed)
                return
            await interaction.followup.send("This server has XP disabled!")
            return

        if user == None:
            user = interaction.user
        data, xpinfo = xp(False, interaction.guild, user=user)

        if data:
            currxp, level, nxt_lvl = xpinfo
            nxt_lvl -= currxp
            if has_perms:
                embed.description = f"**Level**: {level}\n**XP**: {currxp}\n**{nxt_lvl} XP** needed."
                embed.set_author(name=f"@{user.name}'s XP for {interaction.guild.name}.", icon_url=user.display_avatar.url)
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"**__{user.name}__**\n**Level**: {level}\n**XP**: {currxp}\n**{nxt_lvl} XP** needed.")
        else:
            if has_perms:
                embed.set_author(name=f"@{user.name} has no XP {f"{f"for {interaction.guild.name}" if not interaction.guild.name == "" else "as an external app"}"}", icon_url=user.display_avatar.url)
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"**__{user.name}__** has no XP for {interaction.guild.name}.")

    @app_commands.command(name="set_rank", description="Modify a user's rank!")
    @app_commands.describe(user="User to modify", newlevel="Change the user's level", newxp="Change the user's XP", add="Add to current xp, else change it to value")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @canUse()
    @xpEnabledOnly()
    async def set_rank(self, interaction: discord.Interaction, user: discord.Member, newlevel: int = None, newxp: int = None, add: bool = False):
        print(log(False,
                      f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id} ({interaction.guild.name})!"))
        if not newlevel and not newxp:
            await interaction.response.send_message("Please enter either a Level or XP to modify!", ephemeral=True)
            return
        if user.bot:
            await interaction.response.send_message("You cannot modify a bot's rank!", ephemeral=True)
            return
        hasdata, olddata = xp(False, interaction.guild, user=user)
        text = ""

        if newlevel:
            if add:
                text += f"Added {newlevel} Level{"s" if newlevel > 1 else ""}{f" to user's level. ({olddata[1]} -> {olddata[1] + newlevel})" if hasdata else ""}\n"
            else:
                text += f"Changed Level{f" from {olddata[1]}" if hasdata else ""} to Level {newlevel}\n"
        if newxp:
            if add:
                text += f"Added {newxp} XP{f" to user's XP. ({olddata[0]} -> {olddata[0] + newxp})" if hasdata else ""}\n"
            else:
                text += f"Changed XP{f" from {olddata[0]}" if hasdata else ""} to {newxp} XP\n"
        else:
            newxp = random.randint(nextLevel(olddata[1] + newlevel-1), nextLevel(olddata[1] + newlevel)) if add else random.randint(nextLevel(newlevel-1), nextLevel(newlevel))
            text += f"-# *Set XP from {olddata[0]} to {newxp} to match the level due to no XP changes.*\n"

        data = [newxp, newlevel] if not add else [olddata[0] + newxp if newxp else None, olddata[1] + newlevel if newlevel else None]
        xp(True, interaction.guild, data, user, False)
        await interaction.response.send_message(f"Successfully changed {user.mention}'s rank\n{text}", allowed_mentions=discord.AllowedMentions(users=False))

    @app_commands.command(name="settings", description="Change your settings with the bot!")
    @app_commands.describe(xpmessages="Toggle where you want the XP messages for leveling up!")
    @app_commands.choices(xpmessages=[
        app_commands.Choice(name="Disabled", value="0"),
        app_commands.Choice(name="Enabled (In Servers)", value="1"),
        app_commands.Choice(name="Enabled (In DMs)", value="2")
    ])
    @app_commands.allowed_contexts(True, True, True)
    async def settings(self, interaction: discord.Interaction, xpmessages: app_commands.Choice[str] = None):
        print(log(False,f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="User Settings", color=discord.Color.brand_green())
        embed.set_footer(text=interaction.user.name, icon_url=interaction.user.avatar.url)
        msg = ""

        if xpmessages:
            val = user_settings(True, interaction.user.id, "xpmessage", int(xpmessages.value))
            msg += setting_users["xpmessages"][int(xpmessages.value)] + "\n"

        if msg == "":
            msg = "No user settings were changed!"
        embed.description = msg
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Server(bot))
