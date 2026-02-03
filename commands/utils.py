import discord, psutil, ping3, re, platform
from bot import startup, version, pid
from discord import app_commands
from discord.ext import commands
from Cogs.Methods.asynchronous.methods import get_prefix
from Cogs.Methods.methods import permission_check, imgcol_gen
from Cogs.Classes.DiscordModals import BugReport, BotSuggest
from Cogs.Classes.DiscordViews import ServerInfo
from Cogs.Classes.DiscordButtons import CreditsButton
from resources.arrays import veemoworksdevs, recnetdb
from resources.dictionaries import botbadges, cmduae
from Cogs.Methods.methods import log

ping3.EXCEPTIONS = True

class Utils(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    # Get a list of commands
    async def command_autocomplete(self, interaction: discord.Interaction, current: str):
        choices = []
        for cmd in self.bot.tree.walk_commands():
            if cmd.parent is None and current.lower() in cmd.name.lower():
                choices.append(app_commands.Choice(name=cmd.name, value=cmd.name))
        return choices[:25]

    @app_commands.command(name="whois", description="Get info about a user")
    @app_commands.describe(user="User to get info from", ephemeral="Set to ephemeral?")
    @app_commands.allowed_contexts(True, True, True)
    async def whois(self, interaction: discord.Interaction, user: discord.User = None, ephemeral: bool = True):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        if user == None:
            user = interaction.user
        user = await self.bot.fetch_user(user.id)

        class Buttons(discord.ui.View):
            def __init__(self, user: discord.User):
                super().__init__(timeout=180)
                self.user = user

                self.add_item(discord.ui.Button(label="View Profile (WEB)", url=f"https://discord.com/users/{user.id}", style=discord.ButtonStyle.link, row=1))
                self.add_item(discord.ui.Button(label="View Profile (APP)", url=f"discord://-/users/{user.id}", style=discord.ButtonStyle.link, row=1))

                if user.banner:
                    banner_button = discord.ui.Button(label="View Banner", style=discord.ButtonStyle.primary)
                    banner_button.callback = self.callback
                    self.add_item(banner_button)

            async def on_timeout(self):
                for item in self.children:
                    item.disabled = True
                await interaction.edit_original_response(view=self)

            @discord.ui.button(label="View Avatar", style=discord.ButtonStyle.primary)
            async def avatar_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                embed = discord.Embed(color=discord.Color.brand_green())
                embed.set_image(url=self.user.avatar.url)
                embed.set_author(name=f"@{self.user}", icon_url=self.user.avatar.url)

                view = discord.ui.View()
                view.add_item(
                    discord.ui.Button(label="Image URL", style=discord.ButtonStyle.link, url=self.user.avatar.url))
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

            async def callback(self, interaction: discord.Interaction):
                embed = discord.Embed(color=discord.Color.brand_green())
                embed.set_image(url=self.user.banner.url)
                embed.set_author(name=f"@{self.user}", icon_url=self.user.avatar.url)
                view2 = discord.ui.View()
                view2.add_item(
                    discord.ui.Button(label="Image URL", style=discord.ButtonStyle.link, url=self.user.banner.url))
                await interaction.response.send_message(embed=embed, view=view2, ephemeral=True)

        badges = []
        if user.public_flags:
            for flag, emoji in botbadges.items():
                if getattr(user.public_flags, flag, False):
                    badges.append(emoji)
        badge_text = " ".join(badges) if badges else " "
        created_at = f"<t:{int(user.created_at.timestamp())}:R>"

        if user.id == 333585549837336577:
            badge_text += " <:VeraVeemo:1400816211620659272> <:VeemoworksDev:1400816284526051369> <:Python:1400816361189675038> <:dev:1400815766814589080> <:hypesquad:1400816053675884624> <:partner:1400816107325096016> <:bughunter2:1400815976127135874>"
        elif user.id == 299914704594403329:
            badge_text += " <:Chomperling:1400816246160756809>"
        elif user.id == 566996607455723522:
            badge_text += " <:PedroStudios:1400816325311336478>"
        if user.id in veemoworksdevs:
            badge_text += " <:VeemoworksDev:1400816284526051369>"
            if user.id in recnetdb:
                badge_text += " <:RecNetDB:1401234874848907365>"

        embed = discord.Embed(title=f"{user.name}'s Profile", color=discord.Color.brand_green())
        embed.set_thumbnail(url=user.avatar.url)
        if user.banner:
            embed.set_image(url=user.banner.url)
        embed.add_field(name="Display Name:", value=f"**{user.display_name}**", inline=False)
        embed.add_field(name="Username:", value=f"{user.mention} (`@{user.name}`)", inline=False)
        embed.add_field(name="Account Created:", value=created_at, inline=False)
        embed.add_field(name="Badges:", value=badge_text, inline=False)
        embed.set_footer(text=f"ID: {user.id}")

        await interaction.response.send_message(embed=embed, view=Buttons(user), ephemeral=ephemeral)

    @app_commands.command(name="applications", description="Provides an application for Veemoworks")
    @app_commands.allowed_contexts(True, True, True)
    async def applications(self, interaction: discord.Interaction):
        print(log(False,
                  f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        app_embed = discord.Embed(title="Veemoworks Applications",
                                  description="Hi there!\n"
                                              "We have have an always active application for the Veemoworks project! However sometimes we change the application likely becase we changed to a different provider or our system is full, so make sure to double check with AVeemo if you're unsure.",
                                  color=discord.Color.brand_green())
        app_embed.add_field(name="Link:",
                            value="https://forms.gle/HuKAiytkbuc2e7NG7")
        app_embed.set_footer(text="As of: 19/03/25 (Verified: 01/08/25) | (DD/MM/YY)")
        await interaction.response.send_message(embed=app_embed)

    @app_commands.command(name="stats", description="Get the bot's current stats")
    @app_commands.allowed_contexts(True, True, True)
    async def stats(self, interaction: discord.Interaction):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        embed = discord.Embed(color=discord.Color.brand_green())
        embed.set_author(name="ABotmo v" + version, icon_url=self.bot.user.avatar.url)
        embed.add_field(name="Latency:", value=f"{round(self.bot.latency * 1000)}ms")
        embed.add_field(name="Startup:", value=f"<t:{int(startup.timestamp())}> (<t:{int(startup.timestamp())}:R>)")
        embed.add_field(name="Guilds:", value=len(self.bot.guilds))
        embed.add_field(name="Users:", value=len(self.bot.users))
        embed.add_field(name="RAM / Memory:", value=f"{round(psutil.virtual_memory().used / (1024**3), 2)}GB / {round(psutil.virtual_memory().total / (1024**3), 2)}GB")
        embed.add_field(name="CPU:", value=f"{psutil.cpu_percent()}% Util")
        embed.set_footer(text=f"PID {pid} | Python {platform.python_version()} | discord.py V{discord.__version__} | Shard {self.bot.shard_id}")
        class button(discord.ui.View):
            def __init__(self, bot):
                super().__init__(timeout=180)
                self.bot = bot
                self.interaction = interaction
                self.add_item(item=CreditsButton(self.bot))

            async def on_timeout(self):
                for item in self.children:
                    item.disabled = True
                await self.interaction.edit_original_response(view=self)

        await interaction.response.send_message(embed=embed, view=button(self.bot))

    @app_commands.command(name="links", description="Get all links related to the bot")
    @app_commands.allowed_contexts(True, True, True)
    async def invite(self, interaction: discord.Interaction):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.send_message(f"[**`Install Link`**](<https://discord.com/oauth2/authorize?client_id=1399735099452424314> \"Install ABotmo as an External App\") | [**`Source Code`**](<https://github.com/Veemoworks/ABotmo> \"View the code of the bot!\")\n[`Discord Server`](<https://discord.gg/pwXfWfhH7k> \"Join the Discord Server and get access to all features and beta access!\") | [`Donate`](<https://paypal.me/veraveemo> \"Donate to AVeemo to help support them and their project(s)!\") | [`Bot Info`](<https://bot.veraveemo.uk> \"Get all the info from this bot that you need, or just run /help!\")")

    @app_commands.command(name="bugreport", description="Report an ABotmo Bot bug")
    @app_commands.allowed_contexts(True, True, True)
    async def bugreport(self, interaction: discord.Interaction):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.send_modal(BugReport())

    @app_commands.command(name="suggestion", description="Give an ABotmo feature to add")
    @app_commands.allowed_contexts(True, True, True)
    async def suggestion(self, interaction: discord.Interaction):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.send_modal(BotSuggest())

    @app_commands.command(name="help", description="Shows help info and commands")
    @app_commands.describe(command="Command to get help for (* for a list of commands)")
    @app_commands.autocomplete(command=command_autocomplete)
    @app_commands.allowed_contexts(True, True, True)
    async def help(self, interaction: discord.Interaction, command: str = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.defer(ephemeral=True)
        cmdid = None
        embed = discord.Embed(color=discord.Color.brand_green())
        if command == None:
            embed.description = f"{"Command prefix in this server" if interaction.guild and not interaction.guild.name == "" else "Default prefix"} is: `{await get_prefix(self.bot, interaction)}`"
            if interaction.guild:
                embed.title = f"{f"Server: {interaction.guild.name}" if not interaction.guild.name == "" else "ABotmo Help"}"
            else:
                embed.title = f"ABotmo help"

        elif command.strip() == "*":
            commands = await self.bot.tree.fetch_commands()
            embed.title = f"List of all ABotmo commands ({len(commands)}):"
            embed.description = ""
            for cmd in commands:
                embed.description += f"**/{cmd.name}**: `{cmd.description if cmd.description else "No Description"}`\n"

        else:
            commands = await self.bot.tree.fetch_commands()
            for cmd in commands:
                if cmd.name == command:
                    cmdid = cmd.id
                    break

            cmd = self.bot.tree.get_command(command)
            if not cmd:
                embed.title = f"Command: /{command}"
                embed.description = f"Command not found!\nTry using the suggestions or * for a list of all commands."
            else:
                details = cmduae[cmd.name]
                embed.title = f"Command: /{cmd.name}"
                embed.description = f"**Description**: {cmd.description or "No Description"}\n**Markdown**: </{cmd.name}:{cmdid}>\n**Usages**:\n/{cmd.name} {details[0]}\n**Example**:\n/{cmd.name} {details[1]}"
                embed.set_footer(text=f"ID: {cmdid} ""| Key: [] = Optional : {} = Required")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="purge", description="Purge messages in this channel.")
    @app_commands.describe(amount="Amount of messages to purge (1–100)", user="Purge messages from a specific user", bots="Delete messages from bots only", embeds="Delete messages with embeds only", files="Delete messages with attachments only", links="Delete messages with links only", mentions="Delete messages with mentions only")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    @permission_check()
    async def purge_slash(self, interaction: discord.Interaction, amount: int, user: discord.User = None, bots: bool = False, embeds: bool = False, files: bool = False, links: bool = False, mentions: bool = False):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.defer(ephemeral=True)

        if amount < 1 or amount > 100:
            await interaction.followup.send(f"Please provide a number between 1 and 100.\n-# Your input: {amount}")
            return

        def check(msg: discord.Message):
            if user and msg.author != user:
                return False
            if bots and not msg.author.bot:
                return False
            if embeds and not msg.embeds:
                return False
            if files and not msg.attachments:
                return False
            if links and not re.search(r"https?://", msg.content):
                return False
            if mentions and not (msg.mentions or msg.role_mentions):
                return False
            return True

        try:
            deleted = await interaction.channel.purge(limit=amount, check=check)
            if not deleted:
                await interaction.followup.send("No messages matched your filters.")
                return

            summary = f"Purged **{len(deleted)}** messages."
            filters_used = []
            if user: filters_used.append(f"user: {user.display_name}")
            if bots: filters_used.append("bots")
            if embeds: filters_used.append("embeds")
            if files: filters_used.append("files")
            if links: filters_used.append("links")
            if mentions: filters_used.append("mentions")

            if filters_used:
                summary += f" *(filters: {', '.join(filters_used)})*"

            await interaction.followup.send(summary)
        except Exception as e:
            await interaction.followup.send(f"Could not purge messages: {e}")
            print(log(True, f"Could not purge messages: {e}"))

    @app_commands.command(name="serverinfo", description="Get information about the server!")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    async def serverinfo(self, interaction: discord.Interaction):
        print(log(False,f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id} ({interaction.guild.name})!"))
        await interaction.response.defer()
        guild = interaction.guild

        embed = discord.Embed(title=guild.name, description=guild.description, color=discord.Color.brand_green())
        embed.set_footer(text=f"ID: {guild.id}")
        if not guild.banner == None:
            embed.set_image(url=guild.banner.url)
        if not guild.icon == None:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown")
        embed.add_field(name="Created At", value=f"<t:{round(guild.created_at.timestamp())}>")
        embed.add_field(name="Vanity Link", value=guild.vanity_url)
        embed.add_field(name="Preferred Locale", value=guild.preferred_locale)
        embed.add_field(name="Verification Level", value=guild.verification_level)
        embed.add_field(name="Server Boosts", value=f"{guild.premium_subscription_count} (Level {guild.premium_tier})")
        embed.add_field(name="Channels", value=f"{len(guild.text_channels)} Text | {len(guild.voice_channels)} Voice | {len(guild.stage_channels)} Stage")
        embed.add_field(name="Categories", value=len(guild.categories))
        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Roles", value=len(guild.roles))
        embed.add_field(name="Emojis", value=len(guild.emojis))
        embed.add_field(name="Stickers", value=len(guild.stickers))

        view = ServerInfo(guild)
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="roleinfo", description="View the info of a role!")
    @app_commands.describe(role="Choose a role to get info from.")
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.guild_only()
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        print(log(False,f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id} ({interaction.guild.name})!"))
        perms = []
        for name, value in iter(role.permissions):
            if value:
                perms.append(name.replace('_', ' ').title())

        embed = discord.Embed(title=role.name, color=role.color)
        embed.add_field(name="ID:", value=role.id, inline=False)
        embed.add_field(name="Color:", value=str(role.color).upper(), inline=False)
        embed.add_field(name="Markdown:", value=f"`{role.mention}`", inline=False)
        embed.add_field(name="Hoisted:", value=role.hoist, inline=False)
        embed.add_field(name="Mentionable:", value=role.mentionable, inline=False)
        embed.add_field(name="Managed:", value=role.managed, inline=False)
        embed.add_field(name="Position:", value=role.position, inline=False)
        embed.add_field(name="Permissions:", value=", ".join(perms) if perms else "None", inline=False)

        if role.icon:
            embed.set_thumbnail(url=role.icon.url)
        elif str(role.color).upper() != "#000000":
            embed.set_thumbnail(url="attachment://" + imgcol_gen(str(role.color)))

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utils(bot))