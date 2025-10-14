import discord
from discord import app_commands
from discord.ext import commands
from Cogs.Methods.methods import log

class Custom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="applyperms", description="Give perms to a user.")
    @app_commands.guilds(1383601268743868528)
    async def applyperms(self, interaction: discord.Interaction, user: discord.Member):
        print(log(False,f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id} ({interaction.guild.name})!"))
        await interaction.response.defer(ephemeral=True)
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.followup.send("You do not have permission to run this command!")
            return

        torem = interaction.guild.get_role(1392367096410669138)
        toapply = interaction.guild.get_role(1383601365464387584)
        success = False

        for role in user.roles:
            if role.id == torem.id:
                await user.remove_roles(torem, reason="Removing old role from /applyperms")
                await interaction.followup.send(f"Removed role <@&{torem.id}> . . .")
                success = True
                break

        if success:
            await user.add_roles(toapply, reason="Adding new role from /applyperms")
            await interaction.edit_original_response(content=f"Removed role <@&{torem.id}> . . .\nApplied <@&{toapply.id}>!")
        else:
            await interaction.followup.send(f"Could not find <@&{torem.id}> in {user.mention}'s roles.")

async def setup(bot):
    await bot.add_cog(Custom(bot))
