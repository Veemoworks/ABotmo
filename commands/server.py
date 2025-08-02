import discord
from discord import app_commands
from discord.ext import commands
from DataBases.database import server_roles
from Cogs.Methods.methods import log
from Cogs.Classes.DiscordViews import Config

class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverconfig", description="Change the configuration of the server for the bot.")
    @app_commands.guild_only()
    async def serverconfig(self, interaction: discord.Interaction):
        print(log(False, f"{interaction.user} ({interaction.user.id}) used {interaction.command.qualified_name} in {interaction.guild.id}!"))
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to run this command!", ephemeral=True)
            return

        embed = discord.Embed(title="Server Configuration",
                              description=f"Welcome to the Server Configuration Panel, {interaction.user.mention}!\n"
                                          "If you are the server owner and scared anyone can access this, don't worry only people with the \"Administrator\" permission can!\n"
                                          "These are currently the following configurations you can do for the bot:",
                              color=discord.Color.brand_green()
                              )
        embed.add_field(name="Mod Roles",
                        value="Select the \"Roles\" dropdown to select roles, select the same role you added to remove it.\n"
                              "You can add multiple and remove multiple roles.",
                        inline=False
                        )
        current_roles = server_roles(False, interaction)
        await interaction.response.send_message(embed=embed, view=Config(interaction, current_roles), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Server(bot))
