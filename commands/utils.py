import discord, psutil, requests, time, ping3
from discord import app_commands
from discord.ext import commands
from Cogs.Methods.asynchronous.methods import get_prefix
from Cogs.Classes.DiscordModals import BugReport, BotSuggest
from resources.arrays import veemoworksdevs, recnetdb
from resources.dictionaries import hosts, script_urls, botbadges, cmduae
from resources.links import avatar
from Cogs.Methods.methods import log
from ping3 import ping

ping3.EXCEPTIONS = True

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Get a list of commands
    async def command_autocomplete(self, interaction: discord.Interaction, current: str):
        choices = []
        for cmd in self.bot.tree.walk_commands():
            if cmd.parent is None and current.lower() in cmd.name.lower():
                choices.append(app_commands.Choice(name=cmd.name, value=cmd.name))
        return choices

    @app_commands.command(name="whois", description="Get info about a user")
    @app_commands.describe(user="User to get info from", ephemeral="Set to ephemeral?")
    async def whois(self, interaction: discord.Interaction, user: discord.User = None, ephemeral: bool = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        if ephemeral == None:
            ephemeral = True
        if user == None:
            user = interaction.user
        user = await self.bot.fetch_user(user.id)

        class Buttons(discord.ui.View):
            def __init__(self, user: discord.User):
                super().__init__(timeout=180)
                self.user = user
                self.add_item(discord.ui.Button(label="View Profile (WEB)", url=f"https://discord.com/users/{user.id}", style=discord.ButtonStyle.link, row=1))
                self.add_item(discord.ui.Button(label="View Profile (CLIENT)", url=f"discord://-/users/{user.id}", style=discord.ButtonStyle.link, row=1))

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
                await interaction.response.send_message(embed=embed, view=view, ephemeral=ephemeral)

            async def callback(self, interaction: discord.Interaction):
                embed = discord.Embed(color=discord.Color.brand_green())
                embed.set_image(url=self.user.banner.url)
                embed.set_author(name=f"@{self.user}", icon_url=self.user.avatar.url)
                view2 = discord.ui.View()
                view2.add_item(
                    discord.ui.Button(label="Image URL", style=discord.ButtonStyle.link, url=self.user.banner.url))
                await interaction.response.send_message(embed=embed, view=view2, ephemeral=ephemeral)

        badges = []
        if user.public_flags:
            for flag, emoji in botbadges.items():
                if getattr(user.public_flags, flag, False):
                    badges.append(emoji)
        badge_text = " ".join(badges) if badges else " "
        created_at = f"<t:{int(user.created_at.timestamp())}:R>"

        if user.id == 333585549837336577:
            badge_text += " <:VeraVeemo:1400816211620659272> <:VeemoworksDev:1400816284526051369> <:RecNetDB:1401234874848907365> <:Python:1400816361189675038> <:dev:1400815766814589080> <:hypesquad:1400816053675884624> <:partner:1400816107325096016> <:bughunter2:1400815976127135874>"
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
        embed.add_field(name="Username:", value=f"`@{user.name}`", inline=False)
        embed.add_field(name="Account Created:", value=created_at, inline=False)
        embed.add_field(name="Badges:", value=badge_text, inline=False)
        embed.set_footer(text=f"ID: {user.id}")

        await interaction.response.send_message(embed=embed, view=Buttons(user), ephemeral=ephemeral)

    @app_commands.command(name="applications", description="Provides an application for Veemoworks")
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

    @app_commands.command(name="status", description="Check the statuses of many services")
    async def status(self, interaction: discord.Interaction):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.defer()
        msg = ""
        amount = 1
        thingy = {
            "CPU": f"{psutil.cpu_percent()}%",
            "RAM": f"{psutil.virtual_memory().percent}%",
            "Disk": f"{psutil.disk_usage('/').percent}%",
            "Battery": f"{int(psutil.sensors_battery().percent)}%" if psutil.sensors_battery() else "N/A",
            "Uptime": f"{int((time.time() - psutil.boot_time()) // 3600)}h {int(((time.time() - psutil.boot_time()) % 3600) // 60)}m",
        }

        try:
            msg += "### Main Server:\n"
            start = time.perf_counter()
            r = requests.get("http://127.0.0.0:8000/health")
            r.raise_for_status()
            end = time.perf_counter()
            elapsed_ms = (end - start) * 1000
            msg += f"✅ {elapsed_ms:.2f}ms\n"
            amount += 1
            msg += "\n**__Stats__**:\n"
            for name, details in thingy.items():
                msg += f"{name}: {details}\n"
        except Exception as ex:
            msg += f"❌ Error: {ex}\n"

        msg += f"### Bot Status:\n✅ {round(self.bot.latency * 1000)} ms\n### Website:\n"
        for name, host in hosts.items():
            try:
                delay = ping(host, timeout=10, unit="ms")
                if delay is None:
                    msg += f"❌ `{name}` No response\n"
                else:
                    msg += f"✅ `{name}` ({int(delay)} ms)\n"
                    amount += 1
            except ping3.errors.Timeout:
                msg += f"❌ `{name}` Timed Out\n"
            except Exception as ex:
                msg += f"❌ `{name}` Error: {ex}\n"

        msg += f"### Python Scripts:\n"

        for name, url in script_urls.items():
            url = f"http://127.0.0.1:{url}/health"
            try:
                start = time.perf_counter()
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                end = time.perf_counter()
                elapsed_ms = (end - start) * 1000
                msg += f"✅ `{name}` ({int(elapsed_ms)} ms)\n"
                amount += 1
            except Exception as ex:
                msg += f"❌ `{name}` Error: {ex}\n"
                
        msg += "❌ `Channel Topic Updater` Shutdown\n❌ `Minecraft Console Link` Shutdown\n"
        embed = discord.Embed(
            title="Server Status",
            description=f"{amount}/{len(hosts) + len(script_urls) + 4} services up and running!\n{msg}",
            color=discord.Color.brand_green()
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="ping", description="Get the bot's current ping")
    async def ping(self, interaction: discord.Interaction):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        embed = discord.Embed(title="Bot is online!", description=f"Latency is {round(self.bot.latency * 1000)}ms!", color=discord.Color.brand_green())
        embed.set_thumbnail(url=avatar)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="links", description="Get all links related to the bot")
    async def invite(self, interaction: discord.Interaction):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.send_message("[**`Install Link`**](<https://bot.veraveemo.uk/invite> \"Install Veemocord™ as an External App\")\n[`Discord Server`](<https://discord.gg/GzWWqHxRap> \"Join the Discord Server and get access to all features and beta access!\") | [`Donate`](<https://ko-fi.com/veraveemo> \"Donate to AVeemo to help support them and their project(s)!\") | [`Bot Info`](<https://bot.veraveemo.uk> \"Get all the info from this bot that you need, or just run /help!\")")

    @app_commands.command(name="bugreport", description="Report a ABotmo Bot bug")
    async def bugreport(self, interaction: discord.Interaction):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.send_modal(BugReport())

    @app_commands.command(name="suggestion", description="Give an ABotmo feature to add")
    async def suggestion(self, interaction: discord.Interaction):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {f"{interaction.guild.id} ({interaction.guild.name})" if interaction.guild else "DMs"}!"))
        await interaction.response.send_modal(BotSuggest())

    @app_commands.command(name="help", description="Shows help info and commands")
    @app_commands.describe(command="Command to get help for")
    @app_commands.autocomplete(command=command_autocomplete)
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
        else:
            commands = await self.bot.tree.fetch_commands()
            for cmd in commands:
                if cmd.name == command:
                    cmdid = cmd.id
                    break

            cmd = self.bot.tree.get_command(command)
            if not cmd:
                embed.title = f"Command: /{command}"
                embed.description = f"Command not found! Try using the suggestions."
            else:
                embed.title = f"Command: /{cmd.name}"
                embed.description = f"**Description**: {cmd.description or "No Description"}\n**Markdown**: </{cmd.name}:{cmdid}>\n{cmduae[cmd.name]}"
                embed.set_footer(text=f"ID: {cmdid} ""| Key: [] = Optional : {} = Required")
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utils(bot))