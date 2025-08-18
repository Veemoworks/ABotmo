import discord
from discord.ui import View, Button, Select
from Cogs.Classes.DiscordButtons import PrefixChangeButton
from DataBases.database import server_roles, modlogchannel


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

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)


class RolePageButton(Button):
    def __init__(self):
        super().__init__(label="Configure Roles", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        guild_roles = [r for r in interaction.guild.roles if not r.is_default()]
        current_roles = server_roles(False, interaction)
        view = RoleConfig(interaction, guild_roles, current_roles, page=0)

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
        visible_channels = [
            c for c in interaction.guild.text_channels
            if c.permissions_for(interaction.user).view_channel
        ]
        current_channel = modlogchannel(False, interaction.guild)
        view = LogConfig(interaction, visible_channels, current_channel, page=0)

        embed = discord.Embed(
            title="Log Channel Configuration",
            description="Select the channel where moderation logs should be sent:",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=view)


class RoleConfig(View):
    def __init__(self, interaction: discord.Interaction, all_roles, configured_roles, page=0):
        super().__init__(timeout=180)
        self.interaction = interaction

        chunks = list(chunk_list(all_roles, 25))
        self.add_item(Role(chunks[page], configured_roles))

        if len(chunks) > 1:
            self.add_item(PageButton("⬅", page - 1, len(chunks), "role", all_roles, configured_roles))
            self.add_item(PageButton("➡", page + 1, len(chunks), "role", all_roles, configured_roles))

        self.add_item(BackButton())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)


class LogConfig(View):
    def __init__(self, interaction: discord.Interaction, all_channels, configured_channel_id, page=0):
        super().__init__(timeout=180)
        self.interaction = interaction

        chunks = list(chunk_list(all_channels, 25))
        self.add_item(Logs(chunks[page], configured_channel_id))

        if len(chunks) > 1:
            self.add_item(PageButton("⬅", page - 1, len(chunks), "log", all_channels, configured_channel_id))
            self.add_item(PageButton("➡", page + 1, len(chunks), "log", all_channels, configured_channel_id))

        self.add_item(BackButton())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)


class PageButton(Button):
    def __init__(self, label: str, page: int, max_pages: int, mode: str, items, config):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.page = page % max_pages
        self.mode = mode
        self.items = items
        self.config = config

    async def callback(self, interaction: discord.Interaction):
        if self.mode == "role":
            view = RoleConfig(interaction, self.items, self.config, page=self.page)
            embed = discord.Embed(
                title="Role Configuration",
                description="Select the moderator roles below:",
                color=discord.Color.green()
            )
        else:
            view = LogConfig(interaction, self.items, self.config, page=self.page)
            embed = discord.Embed(
                title="Log Channel Configuration",
                description="Select the channel where moderation logs should be sent:",
                color=discord.Color.green()
            )

        await interaction.response.edit_message(embed=embed, view=view)


class BackButton(Button):
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


class Logs(Select):
    def __init__(self, channels, configured_channel_id):
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

    async def callback(self, interaction: discord.Interaction):
        change_summary = modlogchannel(True, interaction.guild, int(self.values[0]))
        current_channel = modlogchannel(False, interaction.guild)
        view = LogConfig(interaction, interaction.guild.text_channels, current_channel, page=0)

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
        current_roles = set(server_roles(False, interaction))
        selected_roles = set(self.values)

        added_roles = selected_roles - current_roles
        removed_roles = (set(opt.value for opt in self.options) & current_roles) - selected_roles

        changes = [server_roles(True, interaction, role_id) for role_id in added_roles.union(removed_roles)]
        change_summary = "\n".join(changes) if changes else "No changes made."

        new_config = server_roles(False, interaction)
        view = RoleConfig(interaction, interaction.guild.roles, new_config, page=0)

        embed = discord.Embed(
            title="Role Configuration",
            description=change_summary,
            color=discord.Color.blurple()
        )
        await interaction.response.edit_message(embed=embed, view=view)
