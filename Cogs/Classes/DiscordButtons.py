import discord
from Cogs.Classes.DiscordModals import PrefixChange

class PrefixChangeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Change Prefix", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(PrefixChange())
