import discord
from Cogs.Classes.DiscordButtons import PrefixChangeButton
from DataBases.database import server_roles
from discord.ui import View, Select

# All of discord.ui.view here
class Config(View):
    def __init__(self, interaction: discord.Interaction, configured_roles):
        super().__init__(timeout=180)
        self.interaction = interaction
        self.configured_roles = configured_roles
        self.add_item(Role(interaction.guild.roles, configured_roles))
        self.add_item(PrefixChangeButton())

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)

# ui.Select here due to a circular import in Cogs.Classes.DiscordSelects.py
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
        self.configured_roles = set(configured_roles)

    async def callback(self, interaction: discord.Interaction):
        selected_roles = set(self.values)
        current_roles = set(self.configured_roles)

        added_roles = selected_roles - current_roles
        removed_roles = current_roles - selected_roles

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