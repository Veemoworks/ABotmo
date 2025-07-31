import discord, random, asyncio
from discord import app_commands
from discord.ext import commands
from Cogs.Methods.methods import log

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="silly", description="Get your silliness percentage")
    @app_commands.describe(user="Enter a user")
    async def silly(self, interaction: discord.Interaction, user: discord.Member = None):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id}!"))
        resuser = f"{user.mention} is"
        dynevil = ""
        if user == None:
            user = interaction.user

        if user.id == interaction.user.id:
            resuser = f"{interaction.user.mention}, you are"

        rand = random.randint(0, 115)
        if rand > 100:
            danr = rand - 100
            rand = rand - danr

        if rand == 100:
            dynevil = "__**PURE SILLY!!**__"
        elif rand >= 75:
            dynevil = "**SILLY!!**"
        elif rand >= 50:
            dynevil = "SIILLY!"
        elif rand >= 25:
            dynevil = "silly!"
        else:
            dynevil = "silly."

        evil = discord.Embed(title="Silly Calculator",
                             description=f"This **SILLY** calculator will determine your silliness, {user.mention}...",
                             color=discord.Color.yellow())
        await interaction.response.send_message(embed=evil)
        await asyncio.sleep(2)
        evil.add_field(name=".", value="")
        await interaction.edit_original_response(embed=evil)
        await asyncio.sleep(1)
        evil.remove_field(0)
        evil.add_field(name=". .", value="")
        await interaction.edit_original_response(embed=evil)
        await asyncio.sleep(1)
        evil.remove_field(0)
        evil.add_field(name=". . .", value="")
        await interaction.edit_original_response(embed=evil)
        await asyncio.sleep(1)
        evil.remove_field(0)
        await interaction.edit_original_response(embed=evil)
        await asyncio.sleep(2)
        evil.add_field(name="", value=f"{resuser} {rand}% {dynevil}")
        await interaction.edit_original_response(embed=evil)

async def setup(bot):
    await bot.add_cog(Fun(bot))
