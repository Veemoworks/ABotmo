import discord, requests, json, os
from datetime import datetime
from Cogs.database import server_settings, xp_roles
from resources.dictionaries import headers
from discord.ui import Modal, TextInput

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

class AppealLog(Modal):
    def __init__(self, guild: discord.Guild, case = None, view: discord.ui.View = None, ogInteract: discord.Message = None):
        super().__init__(title="Appeal this Log")
        self.guild = guild
        self.case = case
        if case is None:
            self.add_item(TextInput(
                label="Case No.",
                placeholder="Enter the case number the log message came with",
                id = 0,
            ))
        self.add_item(TextInput(
            label="Reason for Appeal:",
            placeholder="Enter the reason you'd like to appeal your log",
            style=discord.TextStyle.paragraph,
            id = 1,
        ))
        self.add_item(TextInput(
            label="Other:",
            placeholder="Type in anything else you would like to say",
            style=discord.TextStyle.paragraph,
            required=False,
            id = 2,
        ))
        self.add_item(TextInput(
            label="If applicable, do you accept the Rules?",
            placeholder="y/n",
            id = 3,
            max_length=3,
            min_length=1
        ))
        self.ogInteract = ogInteract
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        case = self.case
        if case is None: case = self.find_item(0).value;
        reason = self.find_item(1).value
        other = self.find_item(2).value
        accept = self.find_item(3).value

        if self.view:
            for item in self.view.children:
                item.disabled = True
            if self.ogInteract:
                await self.ogInteract.edit(view=self.view)

        channel = server_settings(False, self.guild, "appeal")
        if channel:
            channel = self.guild.get_channel(channel)
            if channel:
                from Cogs.Classes.DiscordViews import AppealEmbed
                embed = discord.Embed(title="Moderation Appeal", description=f"An appeal was sent by {interaction.user.mention} ({interaction.user.id}) | ({interaction.user.name})", color=discord.Color.green(), timestamp=datetime.now())
                embed.add_field(name="Case No.", value=case)
                embed.add_field(name="Reason:", value=reason or str(None))
                embed.add_field(name="Other Info:", value=other)
                embed.add_field(name="Read and Accepted Rules:", value=accept)
                msg = await channel.send(content="# Status: __OPEN__\n## Votes:\nAccept: **0**\nDecline: **0**", embed=embed)
                await msg.edit(view=AppealEmbed(msg, interaction.user, case))
                await interaction.response.send_message("Appeal successfully sent! Awaiting Moderators response, a message will be sent on the outcome.", ephemeral=True)
            else:
                await interaction.response.send_message(
                    "This server does not have appeals set up! Please contact the Server Owner / Admin to set it up!",
                    ephemeral=True)
        else:
            await interaction.response.send_message("This server does not have appeals set up! Please contact the Server Owner / Admin to set it up!", ephemeral=True)
        del self

class BannedModify(Modal):
    def __init__(self):
        super().__init__(title="Enter a word to ban")
        self.add_item(TextInput(
            label="Banned Word:",
            placeholder="Enter a word, to remove one type in the same word.",
            style=discord.TextStyle.short
        ))

    async def on_submit(self, interaction: discord.Interaction):
        for field in self.children:
            await interaction.response.send_message(server_settings(True, interaction.guild, "banned", field.value), ephemeral=True)

class XPLevel(Modal):
    def __init__(self, role):
        super().__init__(title="Enter a number")
        self.role = role
        self.add_item(TextInput(
            label=f"Level Required for role: {role.name[:17] + "..." if len(role.name) >= 20 else role.name}",
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