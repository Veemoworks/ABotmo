import discord
from discord.ui import Select
from Cogs.Classes.DiscordModals import XPLevel
from Cogs.database import server_settings, server_channels

class Logs(Select):
    def __init__(self, channels, configured_channel_id, channel):
        options = [
            discord.SelectOption(label=c.name, value=str(c.id), default=(c.id == configured_channel_id))
            for c in channels
        ]
        super().__init__(placeholder="Select a Text Channel", min_values=1, max_values=1, options=options)
        self.channel = channel

    async def callback(self, interaction: discord.Interaction):
        from Cogs.Classes.DiscordViews import LogConfig
        embed = discord.Embed(
            title="Log Channel Configuration",
            description=server_channels(True, interaction.guild, self.channel, int(self.values[0])),
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed,
            view=LogConfig(
                interaction,
                interaction.guild.text_channels,
                server_channels(False, interaction.guild, self.channel),
                self.channel,
                page=0
            )
        )

class Appeals(Select):
    def __init__(self, channels, configured_channel_id):
        options = [
            discord.SelectOption(label=c.name, value=c.id, default=(c.id == configured_channel_id))
            for c in channels
        ]
        super().__init__(placeholder="Select a Text Channel", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        from Cogs.Classes.DiscordViews import AppealConfig
        embed = discord.Embed(
            title="Log Channel Configuration",
            description=server_settings(True, interaction.guild, "appeal", int(self.values[0])),
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed,
            view=AppealConfig(
                interaction,
                interaction.guild.text_channels,
                server_settings(False, interaction.guild, "appeal"),
                page=0
            )
        )

class Role(Select):
    def __init__(self, roles, configured_roles):
        options = [
            discord.SelectOption(label=r.name, value=str(r.id), default=(str(r.id) in configured_roles))
            for r in roles
        ]
        super().__init__(placeholder="Select your Mod Roles", min_values=0, max_values=len(options), options=options)

    async def callback(self, interaction: discord.Interaction):
        from Cogs.Classes.DiscordViews import ServerConfigRole

        current_roles = set(server_settings(False, interaction.guild, "roles"))
        selected_roles = set(self.values)

        changes = [
            server_settings(True, interaction.guild, "roles", role_id)
            for role_id in (selected_roles - current_roles)
                           |
            ((set(o.value for o in self.options) & current_roles) - selected_roles)]

        embed = discord.Embed(title="Role Configuration",
                    description="\n".join(changes) if changes else "No changes made.", color=discord.Color.blurple())
        await interaction.response.edit_message(embed=embed,
                                        view=ServerConfigRole(interaction, interaction.guild.roles,
                                                server_settings(False, interaction.guild, "roles"), page=0))

class XPRole(Select):
    def __init__(self, roles):
        super().__init__(placeholder="Select your level up role", min_values=0, max_values=1,
                         options=[discord.SelectOption(label=r.name, value=str(r.id)) for r in roles])

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(XPLevel(interaction.guild.get_role(int(self.values[0]))))