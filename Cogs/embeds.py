import discord
from discord.ext import commands
from resources.dictionaries import devs

creditsEmbed = discord.Embed(title="ABotmo Credits", description="", color=discord.Colour.brand_green())

def setupBotEmbeds(client: commands.Bot):
    creditsEmbed.set_author(name=client.user.name, icon_url=client.user.avatar.url)

    for role, ppl in devs.items():
        creditsEmbed.description += f"\n## __{role}__:\n"
        for dev in ppl:
            s = client.get_user(dev)
            txt = f"- {s.mention} {s.name}" if s else f"- <@{dev}>"
            creditsEmbed.description += txt