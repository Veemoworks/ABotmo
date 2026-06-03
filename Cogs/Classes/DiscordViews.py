import discord
from discord.ui import View, Button, Select
from Cogs.Classes.DiscordButtons import PrefixChangeButton, BugReportSend, BannedWordModify
from Cogs.Classes.DiscordModals import XPLevel
from Cogs.database import server_settings, server_channels
from resources.arrays import logchannels

class AutoBugReport(View):
    def __init__(self, interaction: discord.Interaction, exception):
        super().__init__(timeout=180)
        self.interaction = interaction

        self.add_item(BugReportSend(exception, interaction, self))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)

class ServerInfo(View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=180)
        self.guild = guild
        self.interaction = None

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.interaction:
            await self.interaction.edit_original_response(view=self)

    @discord.ui.button(label="Roles", style=discord.ButtonStyle.blurple)
    async def roles_button(self, interaction: discord.Interaction, button: Button):
        self.interaction = interaction
        roles = [r.mention for r in self.guild.roles if not r.is_default()]
        roles_text = "\n".join(roles) if roles else "No roles found."

        embed = discord.Embed(
            title=f"Server Roles ({len(roles)})",
            description=roles_text[:4000],
            color=discord.Color.brand_green()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Channels", style=discord.ButtonStyle.blurple)
    async def channels_button(self, interaction: discord.Interaction, button: Button):
        self.interaction = interaction
        text_channels = [c.mention for c in self.guild.text_channels]
        voice_channels = [c.mention for c in self.guild.voice_channels]

        embed = discord.Embed(
            title="Server Channels",
            color=discord.Color.brand_green()
        )
        embed.add_field(
            name=f"Text Channels ({len(text_channels)})",
            value="\n".join(text_channels)[:1024] or "None",
            inline=False
        )
        embed.add_field(
            name=f"Voice Channels ({len(voice_channels)})",
            value="\n".join(voice_channels)[:1024] or "None",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Emojis", style=discord.ButtonStyle.blurple)
    async def emojis_button(self, interaction: discord.Interaction, button: Button):
        emojis = [str(e) for e in self.guild.emojis]
        emojis_text = "".join(emojis)[:4000] if emojis else "No emojis found."

        embed = discord.Embed(
            title=f"Server Emojis ({len(emojis)})",
            description=emojis_text,
            color=discord.Color.brand_green()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

# <editor-fold desc="serverconfig">
def chunk_list(lst, size=25):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

class Config(View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=180)
        self.interaction = interaction

        self.add_item(RolePageButton())
        self.add_item(LogPageButton())
        self.add_item(PrefixChangeButton())
        self.add_item(BannedWordModify())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)

class RolePageButton(Button):
    def __init__(self):
        super().__init__(label="Configure Roles", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        guild_roles = [r for r in interaction.guild.roles if not r.is_default()]
        current_roles = server_settings(False, interaction.guild, "roles")
        view = ServerConfigRole(interaction, guild_roles, current_roles, page=0)

        embed = discord.Embed(
            title="Role Configuration",
            description="Select the moderator roles below:",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=view)

class LogPageButton(Button):
    def __init__(self):
        super().__init__(label="Configure Logs", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        view = LogChoice(interaction)

        embed = discord.Embed(
            title="Log Channel Configuration",
            description="Select the event type of logs:",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=view)

class LogChoice(View):
    def __init__(self, interaction):
        super().__init__(timeout=180)
        self.interaction = interaction

        for channel in logchannels:
            self.add_item(LogChoiceButton(channel))

class LogConfig(View):
    def __init__(self, interaction: discord.Interaction, all_channels, configured_channel_id, channel=None, page=0):
        super().__init__(timeout=180)
        self.interaction = interaction

        chunks = list(chunk_list(all_channels, 25))
        self.add_item(Logs(chunks[page], configured_channel_id, channel))

        if len(chunks) > 1:
            self.add_item(PageButton("⬅", page - 1, len(chunks), "log", all_channels, configured_channel_id, channel))
            self.add_item(PageButton("➡", page + 1, len(chunks), "log", all_channels, configured_channel_id, channel))

        self.add_item(ServerConfigBack())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)

class LogChoiceButton(Button):
    def __init__(self, buttontype):
        super().__init__(label=buttontype.capitalize() + "s", style=discord.ButtonStyle.primary)
        self.buttontype = buttontype

    async def callback(self, interaction):
        visible_channels = [
            c for c in interaction.guild.text_channels
            if c.permissions_for(interaction.user).view_channel
        ]
        current_channel = server_channels(False, interaction.guild, self.buttontype)
        view = LogConfig(interaction, visible_channels, current_channel, self.buttontype, page=0)
        embed = discord.Embed(
            title="Log Channel Configuration",
            description=f"Select the channel you'd like to apply all {"" if self.buttontype == "all event" else self.buttontype} events to:",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=view)

class PageButton(Button):
    def __init__(self, label: str, page: int, max_pages: int, mode: str, items, config, channel=None):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.page = page % max_pages
        self.mode = mode
        self.items = items
        self.config = config
        self.channel = channel

    async def callback(self, interaction: discord.Interaction):
        if self.mode == "role":
            view = ServerConfigRole(interaction, self.items, self.config, page=self.page)
            embed = discord.Embed(
                title="Role Configuration",
                description="Select the moderator roles below:",
                color=discord.Color.green()
            )
        else:
            view = LogConfig(interaction, self.items, self.config, self.channel, self.page)
            embed = discord.Embed(
                title="Log Channel Configuration",
                description=f"Select the channel you'd like to apply all {"" if self.channel == "all event" else self.channel} events to:",
                color=discord.Color.green()
            )

        await interaction.response.edit_message(embed=embed, view=view)



class Logs(Select):
    def __init__(self, channels, configured_channel_id, channel):
        options = [
            discord.SelectOption(
                label=channel.name,
                value=str(channel.id),
                default=(channel.id == configured_channel_id)
            )
            for channel in channels
        ]
        super().__init__(
            placeholder="Select a Text Channel",
            min_values=1,
            max_values=1,
            options=options
        )
        self.channel = channel

    async def callback(self, interaction: discord.Interaction):
        change_summary = server_channels(True, interaction.guild, self.channel, int(self.values[0]))
        current_channel = server_channels(False, interaction.guild, self.channel)
        view = LogConfig(interaction, interaction.guild.text_channels, current_channel, self.channel, page=0)

        embed = discord.Embed(
            title="Log Channel Configuration",
            description=change_summary,
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=view)

class Role(Select):
    def __init__(self, roles, configured_roles):
        options = [
            discord.SelectOption(
                label=role.name,
                value=str(role.id),
                default=(str(role.id) in configured_roles)
            )
            for role in roles
        ]
        super().__init__(
            placeholder="Select your Mod Roles",
            min_values=0,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        current_roles = set(server_settings(False, interaction.guild, "roles"))
        selected_roles = set(self.values)

        added_roles = selected_roles - current_roles
        removed_roles = (set(opt.value for opt in self.options)& current_roles) - selected_roles

        changes = [server_settings(True, interaction.guild, "roles", role_id) for role_id in added_roles.union(removed_roles)]
        change_summary = "\n".join(changes) if changes else "No changes made."

        new_config = server_settings(False, interaction.guild, "roles")
        view = ServerConfigRole(interaction, interaction.guild.roles, new_config, page=0)

        embed = discord.Embed(
            title="Role Configuration",
            description=change_summary,
            color=discord.Color.blurple()
        )
        await interaction.response.edit_message(embed=embed, view=view)

class ServerConfigRole(View):
    def __init__(self, interaction: discord.Interaction, all_roles, configured_roles, page=0):
        super().__init__(timeout=180)
        self.interaction = interaction

        chunks = list(chunk_list(all_roles, 25))
        self.add_item(Role(chunks[page], configured_roles))

        if len(chunks) > 1:
            self.add_item(PageButton("⬅", page - 1, len(chunks), "role", all_roles, configured_roles))
            self.add_item(PageButton("➡", page + 1, len(chunks), "role", all_roles, configured_roles))

        self.add_item(ServerConfigBack())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)

class ServerConfigBack(Button):
    def __init__(self):
        super().__init__(label="Go Back", style=discord.ButtonStyle.secondary, row=2)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Server Configuration",
            description=f"Welcome to the Server Configuration Panel, {interaction.user.mention}!\n"
                        "Only Administrators can access this menu.\n\n"
                        "Choose what you’d like to configure below:",
            color=discord.Color.brand_green()
        )
        view = Config(interaction)
        await interaction.response.edit_message(embed=embed, view=view)
# </editor-fold>

# <editor-fold desc="xpconfig">
class XPConfig(View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=180)
        self.interaction = interaction

        self.add_item(XPRoles())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)

class XPRoles(Button):
    def __init__(self):
        super().__init__(label="Level Roles", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        guild_roles = [r for r in interaction.guild.roles if not r.is_default()]
        view = XPRolePage(interaction, guild_roles, page=0)

        embed = discord.Embed(
                title="Level Role Configuration",
                description="Select 1 role from the list of roles below:",
                color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=view)

class XPPageButton(Button):
    def __init__(self, label: str, page: int, max_pages: int, mode: str, items):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.page = page % max_pages
        self.mode = mode
        self.items = items

    async def callback(self, interaction: discord.Interaction):
        if self.mode == "role":
            view = XPRolePage(interaction, self.items, page=self.page)
            embed = discord.Embed(
                title="Level Role Configuration",
                description="Select 1 role from the list of roles below:",
                color=discord.Color.green()
            )
        # else:
        #     view = LogConfig(interaction, self.items, self.channel, self.page)
        #     embed = discord.Embed(
        #         title="Level Up Message Channel Configuration",
        #         description=f"Select 1 channel to send the level up messages to:",
        #         color=discord.Color.green()
        #     )

        await interaction.response.edit_message(embed=embed, view=view)

class XPRole(Select):
    def __init__(self, roles):
        options = [
            discord.SelectOption(
                label=role.name,
                value=str(role.id)
            )
            for role in roles
        ]
        super().__init__(
            placeholder="Select your level up role",
            min_values=0,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(int(self.values[0]))
        await interaction.response.send_modal(XPLevel(role))

class XPRolePage(View):
    def __init__(self, interaction: discord.Interaction, all_roles, page=0):
        super().__init__(timeout=180)
        self.interaction = interaction

        chunks = list(chunk_list(all_roles, 25))
        self.add_item(XPRole(chunks[page]))

        if len(chunks) > 1:
            self.add_item(XPPageButton("⬅", page - 1, len(chunks), "role", all_roles))
            self.add_item(XPPageButton("➡", page + 1, len(chunks), "role", all_roles))

        self.add_item(XPConfigBack())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)

class XPConfigBack(Button):
    def __init__(self):
        super().__init__(label="Go Back", style=discord.ButtonStyle.secondary, row=2)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="XP Configuration",
            description=f"Welcome to the XP Configuration Panel, {interaction.user.mention}!\n"
                        "Only Administrators can access this menu.\n\n"
                        "Choose what you’d like to configure below:",
            color=discord.Color.brand_green()
        )
        view = XPConfig(interaction)
        await interaction.response.edit_message(embed=embed, view=view)
# </editor-fold>

class ProfileButtons(View):
    def __init__(self, user: discord.User, interaction):
        super().__init__(timeout=180)
        self.user = user
        self.interaction = interaction
        self.add_item(Button(label="View Profile (WEB)", url=f"https://discord.com/users/{user.id}",style=discord.ButtonStyle.link, row=1))
        self.add_item(Button(label="View Profile (APP)", url=f"discord://-/users/{user.id}",style=discord.ButtonStyle.link, row=1))

        if user.banner:
            banner = Button(label="View Banner", style=discord.ButtonStyle.primary)
            banner.callback = self.bannerCallback

            self.add_item(banner)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)

    async def bannerCallback(self, interactionc):
        embed = discord.Embed(color=discord.Color.brand_green())
        embed.set_image(url=self.user.banner.url)
        embed.set_author(name=f"@{self.user}", icon_url=self.user.avatar.url)
        await interactionc.response.send_message(embed=embed, view=View().add_item(Button(label="Image URL", style=discord.ButtonStyle.link, url=self.user.banner.url)), ephemeral=True)

    @discord.ui.button(label="View Avatar", style=discord.ButtonStyle.primary)
    async def callback(self, interaction: discord.Interaction,_):
        embed = discord.Embed(color=discord.Color.brand_green())
        embed.set_image(url=self.user.avatar.url)
        embed.set_author(name=f"@{self.user}", icon_url=self.user.avatar.url)
        await interaction.response.send_message(embed=embed, view=View().add_item(Button(label="Image URL", style=discord.ButtonStyle.link, url=self.user.avatar.url)), ephemeral=True)