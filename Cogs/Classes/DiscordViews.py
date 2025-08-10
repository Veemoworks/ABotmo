import discord
from Cogs.Classes.DiscordButtons import PrefixChangeButton
from DataBases.database import server_roles, modlogchannel
from discord.ui import View, Select

# All of discord.ui.view here
def chunk_list(lst, size=25):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

class Config(View):
    def __init__(self, interaction: discord.Interaction, configured_roles=None, configured_channel=None):
        super().__init__(timeout=180)
        self.interaction = interaction
        self.configured_roles = configured_roles or []
        self.configured_channel = configured_channel
        guild_roles = [r for r in interaction.guild.roles if r.name != "@everyone"]
        guild_channels = [c for c in interaction.guild.text_channels]

        for chunk in chunk_list(guild_roles, 25):
            self.add_item(Role(chunk, self.configured_roles))
        self.add_item(Logs(guild_channels, self.configured_channel))
        self.add_item(PrefixChangeButton())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)

# ui.Select here due to a circular import in Cogs.Classes.DiscordSelects.py
class Logs(Select):
    def __init__(self, all_channels, configured_channel_id):
        options = [
            discord.SelectOption(
                label=channel.name,
                value=str(channel.id),
                default=(channel.id == configured_channel_id)
            )
            for channel in all_channels if isinstance(channel, discord.TextChannel)
        ]

        super().__init__(
            placeholder="Select a Text Channel",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected_channel_id = int(self.values[0])
        old_channel_id = modlogchannel(False, interaction)

        if selected_channel_id == old_channel_id:
            change_summary = "No changes made."
        else:
            change_summary = modlogchannel(True, interaction, selected_channel_id)
        view = Config(interaction, configured_channel=modlogchannel(False, interaction))

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