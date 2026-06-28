import discord
from discord.ui import View, Button
from Cogs.Classes.DiscordButtons import ModalButton, OpenViewButton, PageButton, BackButton, BugReportSend, AppealButton
from Cogs.Classes.DiscordModals import PrefixChange, BannedModify
from Cogs.Classes.DiscordSelects import Logs, Role, XPRole, Appeals
from Cogs.database import server_settings, server_channels
from resources.arrays import logchannels

def chunkList(lst, size=25):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

class TimedView(View):
    def __init__(self, interaction, timeout=3600):
        super().__init__(timeout=timeout)
        self.interaction = interaction

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
            del item
        if self.interaction:
            await self.interaction.edit_original_response(view=self)
        del self

class AutoBugReport(TimedView):
    def __init__(self, interaction: discord.Interaction, exception):
        super().__init__(interaction)
        self.add_item(BugReportSend(exception, interaction, self))

class ServerInfo(TimedView):
    def __init__(self, guild: discord.Guild):
        super().__init__(interaction=None)
        self.guild = guild

    @discord.ui.button(label="Roles", style=discord.ButtonStyle.blurple)
    async def roles_button(self, interaction: discord.Interaction, button: Button):
        self.interaction = interaction
        roles = [r.mention for r in self.guild.roles if not r.is_default()]
        embed = discord.Embed(
            title=f"Server Roles ({len(roles)})",
            description="\n".join(roles)[:4000] if roles else "No roles found.",
            color=discord.Color.brand_green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Channels", style=discord.ButtonStyle.blurple)
    async def channels_button(self, interaction: discord.Interaction, button: Button):
        self.interaction = interaction
        text_channels = [c.mention for c in self.guild.text_channels]
        voice_channels = [c.mention for c in self.guild.voice_channels]

        embed = discord.Embed(title="Server Channels", color=discord.Color.brand_green())
        embed.add_field(name=f"Text Channels ({len(text_channels)})", value="\n".join(text_channels)[:1024] or "None", inline=False)
        embed.add_field(name=f"Voice Channels ({len(voice_channels)})", value="\n".join(voice_channels)[:1024] or "None", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Emojis", style=discord.ButtonStyle.blurple)
    async def emojis_button(self, interaction: discord.Interaction, button: Button):
        emojis = [str(e) for e in self.guild.emojis]
        embed = discord.Embed(
            title=f"Server Emojis ({len(emojis)})",
            description="".join(emojis)[:4000] if emojis else "No emojis found.",
            color=discord.Color.brand_green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# <editor-fold desc="serverconfig">
def configEmbed(user):
    return discord.Embed(
        title="Server Configuration",
        description=f"Welcome to the Server Configuration Panel, {user.mention}!\n"
                    "Only Administrators can access this menu.\n\n"
                    "Choose what you’d like to configure below:",
        color=discord.Color.brand_green()
    )

def roleConfig(interaction, page=0):
    return (discord.Embed(title="Role Configuration",
                         description="Select the moderator roles below:",
                         color=discord.Color.green()),
            ServerConfigRole(
                interaction,
                [r for r in interaction.guild.roles if not r.is_default()],
                server_settings(False, interaction.guild, "roles"), page)
            )

def logEmbed(interaction):
    return discord.Embed(title="Log Channel Configuration", description="Select the event type of logs:",
                         color=discord.Color.green()), LogChoice(interaction)

def logConfig(interaction, channel, page=0):
    return (discord.Embed(
        title="Log Channel Configuration",
        description=f"Select the channel you'd like to apply all {"" if channel == "all event" else channel} events to:",
        color=discord.Color.green()),
            LogConfig(interaction,
                      [c for c in interaction.guild.text_channels if c.permissions_for(interaction.user).view_channel],
                      server_channels(False, interaction.guild, channel), channel, page
            )
    )

def appealConfig(interaction, page=0):
    return (discord.Embed(
        title="Appeal System Configuration",
        description="Select a channel you'd want the appeal embeds to be sent to.",
        color=discord.Color.green()),
            AppealConfig(interaction,
                    [c for c in interaction.guild.text_channels if c.permissions_for(interaction.user).view_channel],
                    server_settings(False, interaction.guild, "appeal"), page
            )
    )

class Config(TimedView):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(interaction)
        self.add_item(OpenViewButton("Moderator Roles", roleConfig))
        self.add_item(OpenViewButton("Configure Logs", logEmbed))
        self.add_item(OpenViewButton("Appeal System", appealConfig))
        self.add_item(ModalButton("Change Prefix", PrefixChange, 2))
        self.add_item(ModalButton("Banned Words", BannedModify, 2))

class LogChoice(TimedView):
    def __init__(self, interaction):
        super().__init__(interaction)
        for channel in logchannels:
            self.add_item(OpenViewButton(channel.capitalize() + "s", lambda i, c=channel: logConfig(i, c), row=None))

class LogConfig(TimedView):
    def __init__(self, interaction: discord.Interaction, all_channels, configured_channel_id, channel=None, page=0):
        super().__init__(interaction)
        chunks = list(chunkList(all_channels, 25))
        self.add_item(Logs(chunks[page], configured_channel_id, channel))

        if len(chunks) > 1:
            paginate = lambda i, p, c=channel: logConfig(i, c, p)
            self.add_item(PageButton("⬅", page - 1, len(chunks), paginate))
            self.add_item(PageButton("➡", page + 1, len(chunks), paginate))

        self.add_item(BackButton(lambda i: (configEmbed(i.user), Config(i))))

class AppealConfig(TimedView):
    def __init__(self, interaction: discord.Interaction, all_channels, configured_channel_id, page = 0):
        super().__init__(interaction)
        chunks = list(chunkList(all_channels, 25))
        self.add_item(Appeals(chunks[page], configured_channel_id))

        if len(chunks) > 1:
            paginate = lambda i, p: appealConfig(i, p)
            self.add_item(PageButton("⬅", page - 1, len(chunks), paginate))
            self.add_item(PageButton("➡", page + 1, len(chunks), paginate))

        self.add_item(BackButton(lambda i: (configEmbed(i.user), Config(i))))

class ServerConfigRole(TimedView):
    def __init__(self, interaction: discord.Interaction, all_roles, configured_roles, page=0):
        super().__init__(interaction)
        chunks = list(chunkList(all_roles, 25))
        self.add_item(Role(chunks[page], configured_roles))

        if len(chunks) > 1:
            self.add_item(PageButton("⬅", page - 1, len(chunks), roleConfig))
            self.add_item(PageButton("➡", page + 1, len(chunks), roleConfig))

        self.add_item(BackButton(lambda i: (configEmbed(i.user), Config(i))))
# </editor-fold>

# <editor-fold desc="xpconfig">
def xpEmbed(user):
    return discord.Embed(
        title="XP Configuration",
        description=f"Welcome to the XP Configuration Panel, {user.mention}!\n"
                    "Only Administrators can access this menu.\n\n"
                    "Choose what you’d like to configure below:",
        color=discord.Color.brand_green()
    )

def xpRoles(interaction, page=0):
    return (discord.Embed(title="Level Role Configuration",
                          description="Select 1 role from the list of roles below:",
                          color=discord.Color.green()),
            XPRolePage(interaction, [r for r in interaction.guild.roles if not r.is_default()], page))

class XPConfig(TimedView):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(interaction)
        self.add_item(OpenViewButton("Level Roles", xpRoles))

class XPRolePage(TimedView):
    def __init__(self, interaction: discord.Interaction, all_roles, page=0):
        super().__init__(interaction)
        chunks = list(chunkList(all_roles, 25))
        self.add_item(XPRole(chunks[page]))

        if len(chunks) > 1:
            self.add_item(PageButton("⬅", page - 1, len(chunks), xpRoles))
            self.add_item(PageButton("➡", page + 1, len(chunks), xpRoles))

        self.add_item(BackButton(lambda i: (xpEmbed(i.user), XPConfig(i))))
# </editor-fold>

class ProfileButtons(TimedView):
    def __init__(self, user: discord.User, interaction):
        super().__init__(interaction)
        self.user = user
        self.add_item(Button(label="View Profile (WEB)", url=f"https://discord.com/users/{user.id}", style=discord.ButtonStyle.link, row=1))
        self.add_item(Button(label="View Profile (APP)", url=f"discord://-/users/{user.id}", style=discord.ButtonStyle.link, row=1))

        if user.banner:
            banner = Button(label="View Banner", style=discord.ButtonStyle.primary)
            banner.callback = self.bannerCallback
            self.add_item(banner)

    async def bannerCallback(self, interactionc):
        embed = discord.Embed(color=discord.Color.brand_green())
        embed.set_image(url=self.user.banner.url)
        embed.set_author(name=f"@{self.user}", icon_url=self.user.avatar.url)
        await interactionc.response.send_message(embed=embed, view=View().add_item(Button(label="Image URL", style=discord.ButtonStyle.link, url=self.user.banner.url)), ephemeral=True)

    @discord.ui.button(label="View Avatar", style=discord.ButtonStyle.primary)
    async def callback(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(color=discord.Color.brand_green())
        embed.set_image(url=self.user.avatar.url)
        embed.set_author(name=f"@{self.user}", icon_url=self.user.avatar.url)
        await interaction.response.send_message(embed=embed, view=View().add_item(Button(label="Image URL", style=discord.ButtonStyle.link, url=self.user.avatar.url)), ephemeral=True)

class AppealEmbed(View):
    def __init__(self, interaction: discord.Message, user: discord.Member | discord.User, case: str):
        super().__init__(timeout=None)

        self.add_item(AppealButton(interaction, "Accept", 1))
        self.add_item(AppealButton(interaction, "Decline", 0))
        self.add_item(AppealButton(interaction, "Close", 2, discord.ButtonStyle.secondary, 2, self, user, case))