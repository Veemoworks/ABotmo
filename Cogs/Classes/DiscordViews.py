import discord
from Cogs.Classes.DiscordButtons import PrefixChange
from DataBases.database import server_roles, modlogchannel
from discord.ui import View, Select

# All of discord.ui.view here
def chunk_list(lst, size=25):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

class Config(View):
    def __init__(self, interaction: discord.Interaction, configured_roles):
        super().__init__(timeout=180)
        self.interaction = interaction
        self.configured_roles = configured_roles
        guild_roles = interaction.guild.roles
        guild_roles = [r for r in guild_roles if r.name != "@everyone"]
        guild_channels = interaction.guild.text_channels
        guild_channels = [r for r in guild_channels]

        for chunk in chunk_list(guild_roles, 25):
            self.add_item(Role(chunk, configured_roles))
        for chunk in chunk_list(guild_channels, 25):
            self.add_item(Logs(chunk, configured_roles))
        self.add_item(PrefixChange())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)

# ui.Select here due to a circular import in Cogs.Classes.DiscordSelects.py
class Logs(Select):
    def __init__(self, all_channels, configured_channel):
        options = []
        for channel in all_channels:
            if not channel.is_news() and not channel.is_nsfw():
                options.append(
                    discord.SelectOption(
                        label=channel.name,
                        value=str(channel.id),
                        default=str(channel.id) in configured_channel
                    )
                )
        super().__init__(
            placeholder="Channel",
            min_values=0,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        current_roles = set(modlogchannel(False, interaction))
        selected_roles = set(self.value)

        added_roles = selected_roles - current_roles
        removed_roles = (set(opt.value for opt in self.options) & current_roles) - selected_roles

        changes = []
        for role_id in added_roles.union(removed_roles):
            msg = modlogchannel(True, interaction, role_id)
            changes.append(msg)

        new_config = modlogchannel(False, interaction)
        view = Config(interaction, new_config)
        change_summary = "\n".join(changes) if changes else "No changes made."

        await interaction.response.edit_message(
            content=change_summary,
            view=view
        )

class Role(Select):
    def __init__(self, all_roles, configured_roles):
        options = []
        for role in all_roles:
            if not role.is_default():
                options.append(
                    discord.SelectOption(
                        label=role.name,
                        value=str(role.id),
                        default=str(role.id) in configured_roles
                    )
                )
        super().__init__(
            placeholder="Roles",
            min_values=0,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        current_roles = set(server_roles(False, interaction))
        selected_roles = set(self.values)

        added_roles = selected_roles - current_roles
        removed_roles = (set(opt.value for opt in self.options) & current_roles) - selected_roles

        changes = []
        for role_id in added_roles.union(removed_roles):
            msg = server_roles(True, interaction, role_id)
            changes.append(msg)

        new_config = server_roles(False, interaction)
        view = Config(interaction, new_config)
        change_summary = "\n".join(changes) if changes else "No changes made."

        await interaction.response.edit_message(
            content=change_summary,
            view=view
        )