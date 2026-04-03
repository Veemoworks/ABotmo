import discord, requests, os, json
from Cogs.Classes.DiscordModals import PrefixChange, BannedModify
from resources.dictionaries import headers, devs

# All of discord.ui.button here
class PrefixChangeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Change Prefix", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(PrefixChange())

class BannedWordModify(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Banned Words", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(BannedModify())

class BugReportSend(discord.ui.Button):
    def __init__(self, exception, interaction, view):
        super().__init__(label="Send Bug Report", style=discord.ButtonStyle.primary)
        self.error = exception
        self.interaction = interaction
        self.oldview = view

    async def callback(self, interaction):
        embed = discord.Embed(color=discord.Color.yellow())
        embed.add_field(name="Command", value="/" + self.interaction.command.qualified_name, inline=False)
        embed.add_field(name="Short Summary", value=self.error, inline=False)
        embed.add_field(name="Reproduction Steps", value="None, automatic bug report via button.", inline=False)
        embed.add_field(name="May we possibly contact you for more info?", value="Yes", inline=False)
        embed.set_author(name=self.interaction.user.display_name, icon_url=self.interaction.user.display_avatar.url)

        await self.interaction.followup.send("Thank you so much for helping ABotmo improve, our devs will look at your bug report as soon as possible! (We may contact you for info)", ephemeral=True)

        data = {
            "content": f"A bug report was submitted by {self.interaction.user.mention} ({self.interaction.user.id})",
            "embeds": [embed.to_dict()]
        }

        try:
            requests.post(os.getenv("BUGWEBHOOK"), data=json.dumps(data), headers=headers)
        except requests.RequestException as e:
            print(f"Failed to send bugreport: {e}")

        for item in self.oldview:
            item.disabled = True
        await self.interaction.edit_original_response(view=self.oldview)

class CreditsButton(discord.ui.Button):
    def __init__(self, bot):
        super().__init__(style=discord.ButtonStyle.primary, label="Credits")
        self.bot = bot

    async def callback(self, interaction):
        await interaction.response.defer()
        embed = discord.Embed(title="ABotmo Credits", description="", color=discord.Colour.brand_green())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)

        for role, ppl in devs.items():
            embed.description += f"\n## __{role}__:\n"
            for dev in ppl:
                dev = self.bot.get_user(dev)
                embed.description += f"- {dev.mention} {dev.name}"

        await interaction.followup.send(embed=embed)
        self.disabled = True
        await interaction.edit_original_response(view=self.view)