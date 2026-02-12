import discord, requests, json, os, dotenv
from DataBases.database import server_settings, xp_roles
from resources.dictionaries import headers
from discord.ui import Modal, TextInput
dotenv.load_dotenv(".env")

# All of discord.ui.modal here
class BugReport(Modal):
    def __init__(self):
        super().__init__(title="Send a bug report")

        self.add_item(TextInput(
            label="Command",
            placeholder="Tell us what ABotmo command you used.",
            style=discord.TextStyle.short
        ))
        self.add_item(TextInput(
            label="Short Summary",
            placeholder="Tell us a short summary of what went wrong.",
            style=discord.TextStyle.short
        ))
        self.add_item(TextInput(
            label="Reproduction Steps",
            placeholder="Tell us how the bug is replicated.",
            style=discord.TextStyle.long
        ))
        self.add_item(TextInput(
            label="May we possibly contact you for more info?",
            placeholder="(yes/no)",
            style=discord.TextStyle.short
        ))

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(color=discord.Color.yellow())
        for field in self.children:
            embed.add_field(name=field.label, value=field.value, inline=False)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message("Thank you so much for helping ABotmo improve, our devs will look at your bug report as soon as possible!", ephemeral=True)

        data = {
            "content": f"A bug report was submitted by {interaction.user.mention} ({interaction.user.id})",
            "embeds": [embed.to_dict()]
        }

        try:
            requests.post(os.getenv("BUGWEBHOOK"), data=json.dumps(data), headers=headers)
        except requests.RequestException as e:
            print(f"Failed to send bugreport: {e}")

class BotSuggest(Modal):
    def __init__(self):
        super().__init__(title="Send a bot suggestion")

        self.add_item(TextInput(
            label="Feature Type",
            placeholder="Tell us what type of feature you want to add. (e.g. database, command)",
            style=discord.TextStyle.short
        ))
        self.add_item(TextInput(
            label="Name of Feature",
            placeholder="Give us a name for this new feature.",
            style=discord.TextStyle.short
        ))
        self.add_item(TextInput(
            label="Feature Details",
            placeholder="Explain your feature in extreme details.",
            style=discord.TextStyle.long
        ))
        self.add_item(TextInput(
            label="May we possibly contact you for more info?",
            placeholder="(yes/no)",
            style=discord.TextStyle.short
        ))

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(color=discord.Color.yellow())
        for field in self.children:
            embed.add_field(name=field.label, value=field.value, inline=False)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message("Thank you so much for your suggestion on ABotmo, our devs will look at your suggestion as soon as possible!", ephemeral=True)

        data = {
            "content": f"A bot suggestion was submitted by {interaction.user.mention} ({interaction.user.id})",
            "embeds": [embed.to_dict()]
        }

        try:
            requests.post(os.getenv("SUGGESTWEBHOOK"), data=json.dumps(data), headers=headers)
        except requests.RequestException as e:
            print(f"Failed to send bugreport: {e}")

class PrefixChange(Modal):
    def __init__(self):
        super().__init__(title="Enter a prefix")
        self.add_item(TextInput(
            label="Prefix",
            placeholder="Enter a prefix, default is \";;\"",
            style=discord.TextStyle.short
        ))

    async def on_submit(self, interaction: discord.Interaction):
        for field in self.children:
            await interaction.response.send_message(server_settings(True, interaction.guild, "prefix", field.value), ephemeral=True)

class XPLevel(Modal):
    def __init__(self, role):
        super().__init__(title="Enter a number")
        self.role = role
        self.add_item(TextInput(
            label=f"Level Required for role: {role.name}",
            placeholder="Enter a number, if you enter anything else it'll be ignored.",
            style=discord.TextStyle.short
        ))

    async def on_submit(self, interaction: discord.Interaction):
        for field in self.children:
            if field.value.isnumeric():
                response = xp_roles(True, interaction.guild, field.value, self.role.id)
                if response:
                    response = f"Successfully added {self.role.mention} as a level up reward for level {field.value}!"
                else:
                    response= f"Succesfully replaced the old role for level {field.value} to {self.role.mention}!"
                await interaction.response.send_message(response, ephemeral=True)