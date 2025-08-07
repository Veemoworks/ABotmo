import discord, asyncio, aiohttp
from discord.ext import tasks
from Cogs.Methods.asynchronous.methods import crash
from Cogs.Methods.methods import log

# All bot status related things
async def status(bot):
    while True:
        try:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} {"servers" if len(bot.guilds) > 1 else "server"}"))
            print(log(False, f"Successfully changed status with {len(bot.guilds)} {"servers" if len(bot.guilds) > 1 else "server"}!"))
        except Exception as e:
            await crash(e)
            print(log(False, f"Failed to change status: {e}"))
        await asyncio.sleep(180)

# Log bot ping to a file
@tasks.loop(seconds=300)
async def bot_ping(bot):
    try:
        with open(r"Files\ABotmo_ping.txt", "w") as file:
            file.write(str(round(bot.latency * 1000)))
        print(log(False, f"Wrote bot ping to file! Current ping is {round(bot.latency * 1000)}ms."))
    except Exception as e:
        print(log(True, f"Failed to write bot ping to file!: {e}"))

# Send pings to uptime kuma
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