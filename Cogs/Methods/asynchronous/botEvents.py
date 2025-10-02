import discord, time
from DataBases.database import xp
from Cogs.Methods.asynchronous.methods import crash
from resources.links import warm

# All bot related events

# Prefix command error
async def command_error(ctx, error):
    await crash(error)
    errorembed = discord.Embed(title="Bot Error!",
                               description="An error occurred while running this command!\n### Possible reasons:\n- A freak error. Try again.\n- This command is in beta/outdated.\n- I'm slow at responding, check </status:1399850020668444813>.\n- If this error lasts for days, shoot us a </bugreport:1396647997290319905>!",
                               color=discord.Color.dark_green())
    errorembed.set_thumbnail(url=warm)
    errorembed.add_field(name="Exception:", value=str(error))
    await ctx.reply(embed=errorembed, mention_author=False)

# App command error
async def app_command_error(interaction: discord.Interaction, error):
    if str(error).startswith("The check functions for command "):
        return
    await crash(error)
    errorembed = discord.Embed(title="Bot Error!",
                               description="An error occurred while running this command!\n### Possible reasons:\n- A freak error. Try again.\n- This command is in beta/outdated.\n- I'm slow at responding, check </status:1399850020668444813>.\n- If this error lasts for days, shoot us a </bugreport:1396647997290319905>!",
                               color=discord.Color.dark_green())
    errorembed.set_thumbnail(url=warm)
    errorembed.add_field(name="Exception:", value=str(error))
    try:
        await interaction.response.send_message(embed=errorembed)
    except discord.errors.InteractionResponded:
        await interaction.followup.send(embed=errorembed)

async def message(msg):
    if msg.author.bot:
        return

    guild = msg.guild
    user = msg.author

    lvl_up, lvl = xp(True, guild, int(time.time()), user)

    if lvl_up:
        await msg.reply(f"{msg.author.mention}, you have succesfully leveled up to Level {lvl}!", allowed_mentions=discord.AllowedMentions(roles=False, users=False, replied_user=False), delete_after=8)
