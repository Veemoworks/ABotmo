import discord, aiohttp, os, psutil
from discord.ext import tasks
from Cogs.Methods.asynchronous.methods import crash
from Cogs.Methods.methods import log
from resources.variables import pid

# All bot status related things
@tasks.loop(minutes=3)
async def status(bot):
    try:
        await bot.change_presence(activity=discord.CustomActivity(name=f"Helping {len(bot.guilds)} {'servers' if len(bot.guilds) > 1 else 'server'}"))
        print(log(False, f"Successfully changed status with {len(bot.guilds)} {"servers" if len(bot.guilds) > 1 else "server"}!"))
    except Exception as e:
        await crash(e)
        print(log(False, f"Failed to change status: {e}"))

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

@tasks.loop(hours=1)
async def ramthing():
    p = psutil.Process()
    for process in psutil.process_iter():
        if process.name() == "WindowsTerminal.exe":
            p = process
            break
    usage = (psutil.Process(p.pid).memory_full_info().uss / (1024**2)) + (psutil.Process(pid).memory_full_info().uss / (1024**2))
    if usage >= 4000:
        os.system("cls")
        print(log(False, f"Cleared Console"))
    print(log(False, f"RAM Usage Report: {round((usage / 16000) * 100, 2)}% ({round(usage)}MB / 16000MB)"))