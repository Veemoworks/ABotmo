import discord
from resources.links import warm

class DiscordEmbeds:
    errorembed = discord.Embed(title="Bot Error!", description="An error occurred while running this command!\n### Possible reasons:\n- A freak error. Try again.\n- This command is in beta/outdated.\n- I'm slow at responding, check </status:1396646022314328106>.\n- If this error lasts for days, shoot us a </bugreport:1396647997290319905>!", color=discord.Color.dark_green())
    errorembed.set_thumbnail(url=warm)
