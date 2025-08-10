import discord
from discord.ui import Select

# All of discord.ui.select here
class Logs(Select):
    def __init__(self, all_channels, configured_channel):
        options = []
        for channel in all_channels:
            if not channel.is_default():
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