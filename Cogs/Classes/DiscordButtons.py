import discord, requests, os, json
from resources.dictionaries import headers, devs

currentPolls = {}

class ModalButton(discord.ui.Button):
    def __init__(self, label, modal_cls, row = 1, *args, style=discord.ButtonStyle.secondary):
        super().__init__(label=label, style=style, row=row)
        self.modal_cls = modal_cls
        self.args = args

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(self.modal_cls(*self.args))

class OpenViewButton(discord.ui.Button):
    def __init__(self, label, builder, style=discord.ButtonStyle.primary, row = 1):
        super().__init__(label=label, style=style, row=row)
        self.builder = builder

    async def callback(self, interaction: discord.Interaction):
        embed, view = self.builder(interaction)
        await interaction.response.edit_message(embed=embed, view=view)

class PageButton(OpenViewButton):
    def __init__(self, label, page, max_pages, builder):
        super().__init__(label, lambda i: builder(i, page % max_pages), style=discord.ButtonStyle.secondary)

class BackButton(OpenViewButton):
    def __init__(self, builder):
        super().__init__("Go Back", builder, style=discord.ButtonStyle.secondary, row=2)

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

class AppealButton(discord.ui.Button):
    def __init__(self, interaction: discord.Message, label: str, abType: int, style: discord.ButtonStyle = discord.ButtonStyle.primary, row: int = 1, view: discord.ui.View = None, user: discord.User | discord.Member = None, case: str = None):
        super().__init__(label=label, style=style, row=row)
        self.abType = abType
        self.parView = view
        self.ogInteract = interaction
        msgId = interaction.id
        temp = currentPolls.get(msgId, False)
        if not temp:
            currentPolls[msgId] = {
                0: 0,
                1: 0,
                "voted": [],
            }
            temp = currentPolls.get(msgId)
        self.votes = temp
        self.user = user
        self.case = case

    async def callback(self, interaction: discord.Interaction):
        if self.abType == 2:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("You do not have permission to close this Appeal Poll! You need Administrator", ephemeral=True)
                return
            for item in self.parView.children:
                item.disabled = True
            modSay = "Accept!"
            modSayP = "accepted"
            if self.votes[0] > self.votes[1]: modSay = "Decline."; modSayP = "denied";
            elif self.votes[1] == self.votes[0]: modSay = "Unsure..."; modSayP = "mixed opinions";
            await self.ogInteract.edit(content=f"# Status: __CLOSED__\n## Votes:\nAccept: **{self.votes[1]}**\nDecline: **{self.votes[0]}**\n\nModerators say: {modSay}", view=self.parView)
            del self.votes
            await interaction.response.send_message(f"Successfully closed the poll! Moderators say: {modSay}", ephemeral=True)
            await self.user.send(f"Your appeal for case {self.case} {"was" if modSayP in ["accepted", "denied"] else "had"} {modSayP}!")
            del self.parView
            del self
        else:
            from Cogs.Methods.methods import permCheck
            if permCheck(interaction.guild, interaction.user):
                if interaction.user.id in self.votes["voted"]:
                    await interaction.response.send_message("You have already voted on this appeal poll!", ephemeral=True)
                    return
                self.votes[self.abType] += 1
                self.votes["voted"].append(interaction.user.id)
                await self.ogInteract.edit(content=f"# Status: __OPEN__\n## Votes:\nAccept: **{self.votes[1]}**\nDecline: **{self.votes[0]}**")
                await interaction.response.send_message("Successfully added your vote!", ephemeral=True)
            else:
                await interaction.response.send_message("You do not have permission to vote on this appeal poll!!", ephemeral=True)