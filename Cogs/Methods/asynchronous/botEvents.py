import discord, aiohttp
from discord.ext import tasks
from Cogs.Methods.methods import log
from Cogs.Methods.asynchronous.methods import crash
from resources.links import warm

@tasks.loop(seconds=300)
async def bot_ping(bot):
    try:
        with open(r"..\Files\ABotmo_ping.txt", "w") as file:
            file.write(str(round(bot.latency * 1000)))
        print(log(False, f"Wrote bot ping to file! Current ping is {round(bot.latency * 1000)}ms."))
    except Exception as e:
        print(log(True, f"Failed to write bot ping to file!: {e}"))

@tasks.loop(seconds=297)
async def kuma(bot):
    url = "https://status.veraveemo.uk/api/push/aUxU5PQwVA"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{url}?status=up&ping={round(bot.latency * 1000)}") as resp:
                if resp.status == 200:
                    print(log(False, "[KUMA] Status ping successful"))
                else:
                    print(log(True, f"[KUMA] Unexpected response: {resp.status}"))
    except Exception as e:
        print(log(True, f"[KUMA] Failed to ping: {e}"))
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}?status=down&msg={str(e)}") as resp:
                    print(log(False, f"[KUMA] Sent fail status: {resp.status}"))
        except Exception as e2:
            print(log(True, f"[KUMA] Failed to send fail status: {e2}"))

async def command_error(ctx, error):
    await crash(error)
    errorembed = discord.Embed(title="Bot Error!",
                               description="An error occurred while running this command!\n### Possible reasons:\n- A freak error. Try again.\n- This command is in beta/outdated.\n- I'm slow at responding, check </status:1399850020668444813>.\n- If this error lasts for days, shoot us a </bugreport:1396647997290319905>!",
                               color=discord.Color.dark_green())
    errorembed.set_thumbnail(url=warm)
    errorembed.add_field(name="Exception:", value=str(error))
    await ctx.reply(embed=errorembed, mention_author=False)


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